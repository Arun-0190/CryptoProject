"""
Bybit V5 funding rate service.
Endpoint: https://api.bybit.com/v5/market/tickers?category=linear
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.models.response_models import FundingRateEntry
from app.utils.logger import get_logger
import time
from app.utils.debug import log_debug

logger = get_logger(__name__)

EXCHANGE = "Bybit"


async def fetch_bybit_rates(client: httpx.AsyncClient) -> list[FundingRateEntry]:
    """
    Fetch and normalise Bybit linear (USDT perp) funding rates.

    Bybit returns fundingRate as a decimal fraction (same as Binance).
    Funding interval: every 8 h.
    """
    start_t = time.perf_counter()
    status_code = "UNKNOWN"
    errors = None
    payload: dict = {}
    
    try:
        resp = await client.get(
            settings.BYBIT_TICKERS_URL,
            params={"category": "linear"},
            timeout=settings.HTTP_TIMEOUT_SECONDS,
        )
        status_code = resp.status_code
        resp.raise_for_status()
        payload = resp.json()
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        errors = f"HTTP Error {status_code}: {exc}"
        logger.error("[%s] HTTP error %s: %s", EXCHANGE, status_code, exc)
    except Exception as exc:
        errors = f"Request Failed: {exc}"
        logger.error("[%s] Request failed: %s", EXCHANGE, exc)

    latency = (time.perf_counter() - start_t) * 1000
    ret_code = payload.get("retCode", -1) if payload else -1
    
    if payload and ret_code != 0:
        errors = f"API error retCode={ret_code}: {payload.get('retMsg')}"
        logger.error("[%s] %s", EXCHANGE, errors)

    items: list[dict] = payload.get("result", {}).get("list", []) if payload else []
    results: list[FundingRateEntry] = []
    missing_fields: list[str] = []

    for item in items:
        try:
            symbol: str = item["symbol"]
            if not symbol.endswith("USDT"):
                continue

            funding_rate_raw = item.get("fundingRate", "") or ""
            if funding_rate_raw == "":
                continue
            funding_rate_pct = float(funding_rate_raw) * 100

            next_funding_time_str = item.get("nextFundingTime", "0") or "0"
            next_funding_time = int(next_funding_time_str) if next_funding_time_str else None

            mark_price_str = item.get("markPrice", "") or ""
            mark_price = float(mark_price_str) if mark_price_str else None

            oi_str = item.get("openInterestValue", "") or ""
            oi = float(oi_str) if oi_str else None

            results.append(
                FundingRateEntry(
                    symbol=symbol,
                    exchange=EXCHANGE,
                    funding_rate=round(funding_rate_pct, 6),
                    next_funding_time=next_funding_time,
                    mark_price=mark_price,
                    oi=oi,
                )
            )
        except (KeyError, ValueError, TypeError) as exc:
            missing_fields.append(f"malformed: {exc}")
            logger.warning("[%s] Skipped malformed record: %s | %s", EXCHANGE, item, exc)

    log_debug(
        exchange=EXCHANGE,
        endpoint=settings.BYBIT_TICKERS_URL,
        latency_ms=latency,
        status_code=status_code,
        raw_response=payload,
        parsed_count=len(results),
        missing_fields=missing_fields,
        errors=errors
    )
    
    logger.info("[%s] Fetched %d symbols", EXCHANGE, len(results))
    return results
