"""
Bitget funding rate service.
Endpoint: https://api.bitget.com/api/mix/v1/market/current-fundRate

Bitget returns fundingRate as a decimal fraction.
productType=umcbl → USDT-M perpetuals.
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.models.response_models import FundingRateEntry
from app.utils.logger import get_logger
import time
from app.utils.debug import log_debug

logger = get_logger(__name__)

EXCHANGE = "Bitget"


def _bitget_symbol_to_standard(symbol: str) -> str:
    """
    Convert Bitget symbol to standard format.
    BTCUSDT_UMCBL  →  BTCUSDT
    """
    return symbol.replace("_UMCBL", "").replace("_DMCBL", "")


async def fetch_bitget_rates(client: httpx.AsyncClient) -> list[FundingRateEntry]:
    """Fetch and normalise Bitget USDT-M perpetual funding rates."""
    start_t = time.perf_counter()
    status_code = "UNKNOWN"
    errors = None
    payload: dict = {}
    
    try:
        resp = await client.get(
            settings.BITGET_FUNDING_URL,
            params={"productType": "USDT-FUTURES"},
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
    code = str(payload.get("code", "")) if payload else ""
    
    if payload and code != "00000":
        errors = f"API returned code={code} msg={payload.get('msg')}"
        logger.error("[%s] %s", EXCHANGE, errors)

    items: list[dict] = payload.get("data", []) if payload else []
    results: list[FundingRateEntry] = []
    missing_fields: list[str] = []

    for item in items:
        try:
            raw_symbol: str = item.get("symbol", "") or ""
            if not raw_symbol:
                continue

            # Only USDT margined
            if "UMCBL" not in raw_symbol and not raw_symbol.endswith("USDT"):
                if "USDT" not in raw_symbol:
                    continue

            symbol = _bitget_symbol_to_standard(raw_symbol)

            funding_rate_raw = item.get("fundingRate", "") or ""
            if funding_rate_raw == "":
                continue
            funding_rate_pct = float(funding_rate_raw) * 100

            results.append(
                FundingRateEntry(
                    symbol=symbol,
                    exchange=EXCHANGE,
                    funding_rate=round(funding_rate_pct, 6),
                    next_funding_time=None,
                    mark_price=None,
                    oi=None,
                )
            )
        except (KeyError, ValueError, TypeError) as exc:
            missing_fields.append(f"malformed: {exc}")
            logger.warning("[%s] Skipped malformed record: %s | %s", EXCHANGE, item, exc)

    log_debug(
        exchange=EXCHANGE,
        endpoint=settings.BITGET_FUNDING_URL,
        latency_ms=latency,
        status_code=status_code,
        raw_response=payload,
        parsed_count=len(results),
        missing_fields=missing_fields,
        errors=errors
    )

    logger.info("[%s] Fetched %d symbols", EXCHANGE, len(results))
    return results
