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
    try:
        resp = await client.get(
            settings.BITGET_FUNDING_URL,
            params={"productType": "umcbl"},
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

    code = str(payload.get("code", ""))
    if code != "00000":
        logger.error("[%s] API returned code=%s msg=%s", EXCHANGE, code, payload.get("msg"))
        return []

    items: list[dict] = payload.get("data", [])
    results: list[FundingRateEntry] = []

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
            logger.warning("[%s] Skipped malformed record: %s | %s", EXCHANGE, item, exc)

    logger.info("[%s] Fetched %d symbols", EXCHANGE, len(results))
    return results
