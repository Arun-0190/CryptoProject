"""
Binance Futures funding rate service.
Endpoint: https://fapi.binance.com/fapi/v1/premiumIndex
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.models.response_models import FundingRateEntry
from app.utils.logger import get_logger
import time
from app.utils.debug import log_debug

logger = get_logger(__name__)

EXCHANGE = "Binance"


async def fetch_binance_rates(client: httpx.AsyncClient) -> list[FundingRateEntry]:
    """
    Fetch and normalise Binance USDT-M futures funding rates.

    Binance reports funding_rate as a decimal fraction (e.g. 0.0001 = 0.01 %).
    We multiply by 100 to express in %.
    Funding interval: every 8 h  →  rate is already per-8h.
    """
    start_t = time.perf_counter()
    status_code = "UNKNOWN"
    errors = None
    raw: list[dict] = []
    
    try:
        resp = await client.get(
            settings.BINANCE_FUTURES_URL,
            timeout=settings.HTTP_TIMEOUT_SECONDS,
        )
        status_code = resp.status_code
        resp.raise_for_status()
        raw = resp.json()
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        errors = f"HTTP Error {status_code}: {exc}"
        logger.error("[%s] HTTP error %s: %s", EXCHANGE, status_code, exc)
    except Exception as exc:
        errors = f"Request Failed: {exc}"
        logger.error("[%s] Request failed: %s", EXCHANGE, exc)

    latency = (time.perf_counter() - start_t) * 1000
    results: list[FundingRateEntry] = []
    missing_fields: list[str] = []

    for item in raw:
        try:
            symbol: str = item["symbol"]
            # Only perpetual USDT pairs
            if not symbol.endswith("USDT"):
                continue
            funding_rate_raw = float(item.get("lastFundingRate", 0) or 0)
            funding_rate_pct = funding_rate_raw * 100  # convert to %
            next_funding_time = int(item.get("nextFundingTime", 0) or 0)
            mark_price = float(item.get("markPrice", 0) or 0) or None

            results.append(
                FundingRateEntry(
                    symbol=symbol,
                    exchange=EXCHANGE,
                    funding_rate=round(funding_rate_pct, 6),
                    next_funding_time=next_funding_time if next_funding_time else None,
                    mark_price=mark_price,
                    oi=None,  # premiumIndex endpoint doesn't include OI
                )
            )
        except (KeyError, ValueError, TypeError) as exc:
            missing_fields.append(f"malformed: {exc}")
            logger.warning("[%s] Skipped malformed record: %s | %s", EXCHANGE, item, exc)

    log_debug(
        exchange=EXCHANGE,
        endpoint=settings.BINANCE_FUTURES_URL,
        latency_ms=latency,
        status_code=status_code,
        raw_response=raw,
        parsed_count=len(results),
        missing_fields=missing_fields,
        errors=errors
    )
    
    logger.info("[%s] Fetched %d symbols", EXCHANGE, len(results))
    return results
