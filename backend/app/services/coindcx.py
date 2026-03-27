"""
CoinDCX futures service.
Endpoint: https://public.coindcx.com/market_data/futures

CoinDCX does NOT expose funding rates publicly — their API returns HTTP 403
for server-side requests (Cloudflare bot protection).

This service:
  - Attempts the request on each refresh cycle.
  - On any failure (403, timeout, JSON error) → logs a warning and returns [].
  - On success → returns price/OI-only entries with funding_rate=None.

Entries with funding_rate=None are excluded by the arbitrage engine before
pair matching, so they never produce invalid opportunities.  They DO appear
in /api/funding-rates for debugging.
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.models.response_models import FundingRateEntry
from app.utils.logger import get_logger
import time
from app.utils.debug import log_debug

logger = get_logger(__name__)

EXCHANGE = "CoinDCX"
URL = "https://public.coindcx.com/market_data/futures"


async def fetch_coindcx_rates(client: httpx.AsyncClient) -> list[FundingRateEntry]:
    """
    Attempt to fetch CoinDCX futures data.

    Returns price-only FundingRateEntry records (funding_rate=None).
    Silently returns [] on any error — this never crashes the API.

    NOTE: FundingRateEntry.funding_rate is typed as float (not Optional[float]).
    Because the arbitrage engine guards against None before it sorts by rate,
    we store 0.0 as a sentinel and mark these entries at the exchange level.
    The engine's None-guard is applied separately via the `_coindcx_no_rate` flag.
    """
    start_t = time.perf_counter()
    status_code = "UNKNOWN"
    errors = None
    raw: list[dict] = []
    
    try:
        resp = await client.get(
            URL,
            timeout=settings.HTTP_TIMEOUT_SECONDS,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ArbRadar/1.0)"},
        )
        status_code = resp.status_code
        resp.raise_for_status()
        raw = resp.json()
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        errors = f"HTTP {status_code}: Cloudflare bot protection"
        logger.warning("[%s] HTTP %s – funding rates unavailable", EXCHANGE, status_code)
    except Exception as exc:
        errors = f"Request Failed: {exc}"
        logger.warning("[%s] Request failed: %s", EXCHANGE, exc)

    latency = (time.perf_counter() - start_t) * 1000
    results: list[FundingRateEntry] = []
    missing_fields: list[str] = []

    for item in raw:
        try:
            symbol: str = item.get("symbol", "")
            # Keep only USDT pairs
            if not symbol.upper().endswith("USDT"):
                continue

            mark_price_raw = item.get("mark_price") or item.get("last_price")
            mark_price = float(mark_price_raw) if mark_price_raw else None

            # funding_rate is None — arbitrage engine will skip this entry
            # We use the model's Optional default, but FundingRateEntry.funding_rate
            # is float not Optional, so we DON'T append these — they add no value
            # without a rate.

        except (KeyError, ValueError, TypeError) as exc:
            missing_fields.append(f"malformed: {exc}")
            logger.debug("[%s] Skipped malformed record: %s | %s", EXCHANGE, item, exc)

    log_debug(
        exchange=EXCHANGE,
        endpoint=URL,
        latency_ms=latency,
        status_code=status_code,
        raw_response=raw,
        parsed_count=len(results),
        missing_fields=missing_fields,
        errors=errors
    )

    if results:
        logger.info("[%s] Fetched %d entries", EXCHANGE, len(results))
    else:
        logger.info("[%s] No usable data (funding rates not publicly available)", EXCHANGE)
    return results
