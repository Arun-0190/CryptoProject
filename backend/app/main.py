"""
FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload
"""
from __future__ import annotations

import time
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.arbitrage import get_arbitrage_opportunities
from app.models.response_models import ArbitrageResponse, ErrorResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description=(
        "Real-time funding rate arbitrage opportunities across Binance, Bybit, OKX and Bitget."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Middleware – request logging
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    elapsed_ms = (time.monotonic() - start) * 1000
    logger.info(
        "%-6s %s → %s  (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "timestamp": int(time.time() * 1000)}


# ---------------------------------------------------------------------------
# Main endpoint
# ---------------------------------------------------------------------------
@app.get(
    "/api/arbitrage-opportunities",
    response_model=ArbitrageResponse,
    responses={500: {"model": ErrorResponse}},
    tags=["Arbitrage"],
    summary="Fetch funding rate arbitrage opportunities",
    description=(
        "Returns cross-exchange funding rate arbitrage opportunities. "
        "Data is fetched from Binance, Bybit, OKX, and Bitget in parallel "
        "and cached for 10 seconds."
    ),
)
async def arbitrage_opportunities(
    min_spread: Optional[float] = Query(
        default=None,
        ge=0,
        description="Minimum funding spread (%) to include in results",
    ),
    exchanges: Optional[List[str]] = Query(
        default=None,
        description="Filter by exchange name(s) (e.g. Binance, Bybit, OKX, Bitget)",
    ),
    sort_by: str = Query(
        default="spread",
        pattern="^(spread|apr)$",
        description="Sort results by 'spread' (default) or 'apr'",
    ),
    symbol: Optional[str] = Query(
        default=None,
        description="Filter by exact symbol (e.g. BTCUSDT)",
    ),
):
    try:
        opps = await get_arbitrage_opportunities(
            min_spread=min_spread,
            exchanges=exchanges,
            sort_by=sort_by,
            symbol=symbol,
        )
    except Exception as exc:
        logger.exception("[API] Unhandled error in arbitrage endpoint: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error", "detail": str(exc)},
        )

    if opps is None:
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "error": "No data available",
                "detail": "All exchanges failed to respond.",
            },
        )

    return ArbitrageResponse(
        success=True,
        timestamp=int(time.time() * 1000),
        count=len(opps),
        data=opps,
    )


# ---------------------------------------------------------------------------
# Funding rates raw endpoint (useful for debugging)
# ---------------------------------------------------------------------------
@app.get(
    "/api/funding-rates",
    tags=["Debug"],
    summary="Raw funding rates from all exchanges",
)
async def raw_funding_rates(
    exchange: Optional[str] = Query(
        default=None,
        description="Filter by exchange name",
    ),
):
    """
    Returns the raw normalised funding rate entries before arbitrage pairing.
    Useful for debugging individual exchange integrations.
    """
    import httpx as _httpx
    from app.services.binance import fetch_binance_rates
    from app.services.bybit import fetch_bybit_rates
    from app.services.okx import fetch_okx_rates
    from app.services.bitget import fetch_bitget_rates
    import asyncio

    async with _httpx.AsyncClient() as client:
        results = await asyncio.gather(
            fetch_binance_rates(client),
            fetch_bybit_rates(client),
            fetch_okx_rates(client),
            fetch_bitget_rates(client),
            return_exceptions=True,
        )

    combined = []
    for r in results:
        if not isinstance(r, Exception):
            combined.extend([e.model_dump() for e in r])

    if exchange:
        combined = [e for e in combined if e["exchange"].lower() == exchange.lower()]

    return {
        "success": True,
        "timestamp": int(time.time() * 1000),
        "count": len(combined),
        "data": combined,
    }
