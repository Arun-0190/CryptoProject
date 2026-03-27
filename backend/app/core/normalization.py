"""
Normalisation utilities.

All exchange services produce FundingRateEntry with funding_rate in %.
This module provides:
  - Symbol normalisation helpers (used by exchange services)
  - Grouping / deduplication helpers (used by the arbitrage engine)
"""
from __future__ import annotations

from collections import defaultdict

from app.models.response_models import FundingRateEntry


# ---------------------------------------------------------------------------
# Symbol normalisation
# ---------------------------------------------------------------------------

def normalize_symbol(symbol: str) -> str:
    """
    Strip separators and uppercase.
    Examples:  BTC_USDT → BTCUSDT,  ETH-USD → ETHUSD
    """
    return symbol.replace("_", "").replace("-", "").upper()


def normalize_to_usdt(symbol: str) -> str:
    """
    Treat USD and USDT pairs as equivalent — map USD → USDT.
    Example:  BTCUSD → BTCUSDT
    Only applies to the bare USD suffix (not BUSD, USDC etc.).
    """
    if symbol.endswith("USD") and not symbol.endswith("USDT"):
        return symbol[:-3] + "USDT"
    return symbol


def canonical_symbol(raw: str) -> str:
    """Full normalisation pipeline: strip separators → uppercase → USDT-unify."""
    return normalize_to_usdt(normalize_symbol(raw))


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
