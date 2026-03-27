"""
OKX funding rate service.
Endpoint: https://www.okx.com/api/v5/public/funding-rate?instType=SWAP

OKX returns fundingRate as decimal fraction.
For perpetual swaps the interval is every 8 h.
Note: fundingTime is the timestamp of the *next* settlement.
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.models.response_models import FundingRateEntry
from app.utils.logger import get_logger

logger = get_logger(__name__)

EXCHANGE = "OKX"


def _okx_symbol_to_standard(inst_id: str) -> str | None:
    """
    Convert OKX instrument id to standard symbol format.
    BTC-USDT-SWAP  →  BTCUSDT
    BTC-USD-SWAP   →  skip (coin-margined)
    """
    parts = inst_id.split("-")
    if len(parts) == 3 and parts[2] == "SWAP" and parts[1] == "USDT":
        return parts[0] + "USDT"
    return None


async def fetch_okx_rates(client: httpx.AsyncClient) -> list[FundingRateEntry]:
    """Fetch and normalise OKX perpetual swap funding rates."""
    try:
        resp = await client.get(
            settings.OKX_FUNDING_URL,
            params={"instType": "SWAP"},
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

    code = payload.get("code", "")
    if code != "0":
        logger.error("[%s] API returned code=%s msg=%s", EXCHANGE, code, payload.get("msg"))
        return []

    items: list[dict] = payload.get("data", [])
    results: list[FundingRateEntry] = []

    for item in items:
        try:
            inst_id: str = item.get("instId", "")
            symbol = _okx_symbol_to_standard(inst_id)
            if symbol is None:
                continue

            funding_rate_raw = item.get("fundingRate", "") or ""
            if funding_rate_raw == "":
                continue
            funding_rate_pct = float(funding_rate_raw) * 100

            # fundingTime is next settlement time in ms
            funding_time_str = item.get("fundingTime", "0") or "0"
            next_funding_time = int(funding_time_str) if funding_time_str else None

            results.append(
                FundingRateEntry(
                    symbol=symbol,
                    exchange=EXCHANGE,
                    funding_rate=round(funding_rate_pct, 6),
                    next_funding_time=next_funding_time,
                    mark_price=None,   # not in funding-rate endpoint
                    oi=None,
                )
            )
        except (KeyError, ValueError, TypeError) as exc:
            logger.warning("[%s] Skipped malformed record: %s | %s", EXCHANGE, item, exc)

    logger.info("[%s] Fetched %d symbols", EXCHANGE, len(results))
    return results
