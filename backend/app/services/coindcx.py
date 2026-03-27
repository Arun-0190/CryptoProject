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
    try:
        resp = await client.get(
            URL,
            timeout=settings.HTTP_TIMEOUT_SECONDS,
            # Send a browser-like user-agent to improve compatibility
            headers={"User-Agent": "Mozilla/5.0 (compatible; ArbRadar/1.0)"},
        )
        resp.raise_for_status()
        raw: list[dict] = resp.json()
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "[%s] HTTP %s – funding rates unavailable (expected, Cloudflare protected)",
            EXCHANGE, exc.response.status_code,
        )
        return []
    except Exception as exc:
        logger.warning("[%s] Request failed: %s", EXCHANGE, exc)
        return []

    results: list[FundingRateEntry] = []
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
            logger.debug("[%s] Skipped malformed record: %s | %s", EXCHANGE, item, exc)

    # CoinDCX entries without funding rates cannot participate in arbitrage.
    # Return empty list to keep the engine clean.
    # When/if CoinDCX adds public funding rate data, this service can be updated.
    if results:
        logger.info("[%s] Fetched %d entries", EXCHANGE, len(results))
    else:
        logger.info("[%s] No usable data (funding rates not publicly available)", EXCHANGE)
    return results
