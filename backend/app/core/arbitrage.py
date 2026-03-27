"""
Core arbitrage engine.

Orchestrates:
 1. Parallel data fetch from all exchanges
 2. Grouping by symbol
 3. Finding the best long / short pair per symbol
 4. Computing all metrics
"""
from __future__ import annotations

import asyncio
import time
from typing import Optional

import httpx

from app.config import settings
from app.core.calculations import (
    best_mark_price,
    best_oi,
    compute_apr,
    compute_confidence,
    compute_risk_score,
    earliest_next_funding,
)
from app.core.normalization import deduplicate_by_exchange, group_by_symbol
from app.models.response_models import ArbitrageOpportunity, FundingRateEntry
from app.services.binance import fetch_binance_rates
from app.services.bitget import fetch_bitget_rates
from app.services.bybit import fetch_bybit_rates
from app.services.coindcx import fetch_coindcx_rates
from app.services.delta import fetch_delta_rates
from app.services.okx import fetch_okx_rates
from app.utils.cache import cache
from app.utils.logger import get_logger

logger = get_logger(__name__)

CACHE_KEY = "arbitrage_data"


async def _fetch_all_rates() -> list[FundingRateEntry]:
    """Fetch rates from all exchanges concurrently, returning combined list."""
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            fetch_binance_rates(client),
            fetch_bybit_rates(client),
            fetch_okx_rates(client),
            fetch_bitget_rates(client),
            fetch_delta_rates(client),
            fetch_coindcx_rates(client),
            return_exceptions=True,
        )

    exchange_names = ["Binance", "Bybit", "OKX", "Bitget", "Delta Exchange India", "CoinDCX"]
    combined: list[FundingRateEntry] = []
    for i, result in enumerate(results):
        name = exchange_names[i] if i < len(exchange_names) else f"Exchange[{i}]"
        if isinstance(result, Exception):
            logger.error("[Arbitrage] %s fetch raised exception: %s", name, result)
        else:
            combined.extend(result)

    return combined


def _compute_opportunities(
    entries: list[FundingRateEntry],
) -> list[ArbitrageOpportunity]:
    """
    Given normalised multi-exchange entries, compute all valid arbitrage pairs.
    """
    grouped = group_by_symbol(entries)
    opportunities: list[ArbitrageOpportunity] = []

    for symbol, exchange_entries in grouped.items():
        # Remove duplicates by exchange
        deduped = deduplicate_by_exchange(exchange_entries)

        # --- Guard: skip entries where funding_rate is None (e.g. CoinDCX) ---
        # FundingRateEntry.funding_rate is typed float, so None can't be stored
        # directly — all services that can't supply a rate return [] instead.
        # This guard is a belt-and-suspenders check.
        deduped = [e for e in deduped if e.funding_rate is not None]

        # Need at least 2 exchanges with valid rates to form a pair
        if len(deduped) < 2:
            continue

        # Sort by funding rate ascending
        sorted_entries = sorted(deduped, key=lambda e: e.funding_rate)
        long_entry = sorted_entries[0]   # lowest rate → go long here
        short_entry = sorted_entries[-1]  # highest rate → go short here

        spread = round(short_entry.funding_rate - long_entry.funding_rate, 6)
        if spread <= 0:
            continue

        mark_price = best_mark_price(deduped)
        oi = best_oi(deduped)
        next_funding_time = earliest_next_funding(deduped)
        apr = compute_apr(spread)
        risk = compute_risk_score(spread, oi)
        confidence = compute_confidence(spread, oi)

        opportunities.append(
            ArbitrageOpportunity(
                symbol=symbol,
                long_exchange=long_entry.exchange,
                short_exchange=short_entry.exchange,
                long_rate=long_entry.funding_rate,
                short_rate=short_entry.funding_rate,
                funding_diff=spread,
                apr=apr,
                mark_price=mark_price,
                oi=oi,
                next_funding_time=next_funding_time,
                confidence=confidence,
                risk=risk,
            )
        )

    return opportunities


async def get_arbitrage_opportunities(
    min_spread: Optional[float] = None,
    exchanges: Optional[list[str]] = None,
    sort_by: str = "spread",
    symbol: Optional[str] = None,
) -> list[ArbitrageOpportunity]:
    """
    High-level function called by the API endpoint.

    Uses cache with TTL. Applies filters and sorting before returning.
    """
    # Try cache first
    cached = cache.get(CACHE_KEY)
    if cached is None:
        logger.info("[Arbitrage] Cache miss – fetching live data")
        entries = await _fetch_all_rates()

        if not entries:
            logger.error("[Arbitrage] All exchanges returned no data")
            return []

        opportunities = _compute_opportunities(entries)
        cache.set(CACHE_KEY, opportunities, ttl=settings.CACHE_TTL_SECONDS)
        logger.info("[Arbitrage] Computed %d opportunities, cached for %ds",
                    len(opportunities), settings.CACHE_TTL_SECONDS)
    else:
        opportunities = cached
        logger.debug("[Arbitrage] Serving %d opportunities from cache", len(opportunities))

    # --- Filtering ---
    result = opportunities

    if symbol:
        sym_upper = symbol.upper()
        result = [o for o in result if o.symbol == sym_upper]

    if min_spread is not None:
        result = [o for o in result if o.funding_diff >= min_spread]

    if exchanges:
        exchange_set = {e.lower() for e in exchanges}
        result = [
            o for o in result
            if o.long_exchange.lower() in exchange_set
            or o.short_exchange.lower() in exchange_set
        ]

    # --- Sorting ---
    if sort_by == "apr":
        result = sorted(result, key=lambda o: o.apr, reverse=True)
    else:  # default: spread
        result = sorted(result, key=lambda o: o.funding_diff, reverse=True)

    return result
