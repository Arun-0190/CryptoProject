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
import time
from app.utils.debug import log_debug

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
    start_t = time.perf_counter()
    status_code = "UNKNOWN"
    errors = None
    payload: dict = {}
    
    try:
        resp = await client.get(
            settings.OKX_FUNDING_URL,
            params={"instType": "SWAP"},
            timeout=3.0,  # Hardcapped to 3s to prevent 10s stall from regional ISP blocking
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
    code = payload.get("code", "") if payload else ""
    
    if payload and code != "0":
        errors = f"API returned code={code} msg={payload.get('msg')}"
        logger.error("[%s] %s", EXCHANGE, errors)

    items: list[dict] = payload.get("data", []) if payload else []
    results: list[FundingRateEntry] = []
    missing_fields: list[str] = []

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
            missing_fields.append(f"malformed: {exc}")
            logger.warning("[%s] Skipped malformed record: %s | %s", EXCHANGE, item, exc)

    log_debug(
        exchange=EXCHANGE,
        endpoint=settings.OKX_FUNDING_URL,
        latency_ms=latency,
        status_code=status_code,
        raw_response=payload,
        parsed_count=len(results),
        missing_fields=missing_fields,
        errors=errors
    )

    logger.info("[%s] Fetched %d symbols", EXCHANGE, len(results))
    return results
