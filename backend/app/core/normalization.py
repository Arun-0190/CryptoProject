"""
Normalisation utilities.

All exchange services already produce FundingRateEntry with funding_rate in %.
This module provides grouping helpers used by the arbitrage engine.
"""
from __future__ import annotations

from collections import defaultdict

from app.models.response_models import FundingRateEntry


def group_by_symbol(
    entries: list[FundingRateEntry],
) -> dict[str, list[FundingRateEntry]]:
    """
    Group a flat list of FundingRateEntry records by symbol.

    Returns a dict: { "BTCUSDT": [entry_binance, entry_bybit, ...], ... }
    """
    grouped: dict[str, list[FundingRateEntry]] = defaultdict(list)
    for entry in entries:
        grouped[entry.symbol].append(entry)
    return dict(grouped)


def deduplicate_by_exchange(
    entries: list[FundingRateEntry],
) -> list[FundingRateEntry]:
    """
    If the same exchange appears multiple times for a symbol (shouldn't happen
    but defensive), keep only the first occurrence.
    """
    seen: set[str] = set()
    result: list[FundingRateEntry] = []
    for e in entries:
        if e.exchange not in seen:
            seen.add(e.exchange)
            result.append(e)
    return result
