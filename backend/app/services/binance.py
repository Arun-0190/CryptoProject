"""
Binance Futures funding rate service.
Endpoint: https://fapi.binance.com/fapi/v1/premiumIndex
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.models.response_models import FundingRateEntry
from app.utils.logger import get_logger

logger = get_logger(__name__)

EXCHANGE = "Binance"


async def fetch_binance_rates(client: httpx.AsyncClient) -> list[FundingRateEntry]:
    """
    Fetch and normalise Binance USDT-M futures funding rates.

    Binance reports funding_rate as a decimal fraction (e.g. 0.0001 = 0.01 %).
    We multiply by 100 to express in %.
    Funding interval: every 8 h  →  rate is already per-8h.
    """
    try:
        resp = await client.get(
            settings.BINANCE_FUTURES_URL,
            timeout=settings.HTTP_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        raw: list[dict] = resp.json()
    except httpx.HTTPStatusError as exc:
        logger.error("[%s] HTTP error %s: %s", EXCHANGE, exc.response.status_code, exc)
        return []
    except Exception as exc:
        logger.error("[%s] Request failed: %s", EXCHANGE, exc)
        return []

    results: list[FundingRateEntry] = []
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
            logger.warning("[%s] Skipped malformed record: %s | %s", EXCHANGE, item, exc)

    logger.info("[%s] Fetched %d symbols", EXCHANGE, len(results))
    return results
