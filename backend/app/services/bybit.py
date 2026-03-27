"""
Bybit V5 funding rate service.
Endpoint: https://api.bybit.com/v5/market/tickers?category=linear
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.models.response_models import FundingRateEntry
from app.utils.logger import get_logger

logger = get_logger(__name__)

EXCHANGE = "Bybit"


async def fetch_bybit_rates(client: httpx.AsyncClient) -> list[FundingRateEntry]:
    """
    Fetch and normalise Bybit linear (USDT perp) funding rates.

    Bybit returns fundingRate as a decimal fraction (same as Binance).
    Funding interval: every 8 h.
    """
    try:
        resp = await client.get(
            settings.BYBIT_TICKERS_URL,
            params={"category": "linear"},
            timeout=settings.HTTP_TIMEOUT_SECONDS,
        )
        resp.raise_for_status()
        payload: dict = resp.json()
    except httpx.HTTPStatusError as exc:
        logger.error("[%s] HTTP error %s: %s", EXCHANGE, exc.response.status_code, exc)
        return []
    except Exception as exc:
        logger.error("[%s] Request failed: %s", EXCHANGE, exc)
        return []

    ret_code = payload.get("retCode", -1)
    if ret_code != 0:
        logger.error("[%s] API error retCode=%s: %s", EXCHANGE, ret_code, payload.get("retMsg"))
        return []

    items: list[dict] = payload.get("result", {}).get("list", [])
    results: list[FundingRateEntry] = []

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
            logger.warning("[%s] Skipped malformed record: %s | %s", EXCHANGE, item, exc)

    logger.info("[%s] Fetched %d symbols", EXCHANGE, len(results))
    return results
