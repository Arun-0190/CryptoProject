"""
Financial calculations for arbitrage metrics.
"""
from __future__ import annotations

from app.models.response_models import FundingRateEntry


# Binance/Bybit/OKX/Bitget all settle every 8 hours → 3 times per day
FUNDINGS_PER_DAY = 3
DAYS_PER_YEAR = 365


def compute_apr(spread_pct: float) -> float:
    """
    Annualise the 8-hour funding spread.

    apr = spread(%) × fundings_per_day × days_per_year
    """
    return round(spread_pct * FUNDINGS_PER_DAY * DAYS_PER_YEAR, 4)


def compute_estimated_profit(spread_pct: float, position_size: float) -> float:
    """
    Estimated profit per funding event for a given notional position size (USD).

    profit = (spread / 100) × position_size
    """
    return round((spread_pct / 100) * position_size, 6)


def compute_risk_score(
    spread_pct: float,
    oi: float | None,
) -> str:
    """
    Heuristic risk assessment.

    Low   → high OI and moderate-to-large spread (liquid market, easy to exit)
    High  → very low OI or tiny spread (illiquid or marginal opportunity)
    """
    if oi is None:
        # No OI data → conservative
        if spread_pct >= 0.05:
            return "Medium"
        return "High"

    if oi >= 5_000_000 and spread_pct >= 0.02:
        return "Low"
    if oi >= 1_000_000 and spread_pct >= 0.01:
        return "Medium"
    return "High"


def compute_confidence(
    spread_pct: float,
    oi: float | None,
) -> str:
    """
    Confidence level for the arbitrage opportunity.

    High   → large spread + high OI
    Medium → moderate spread or moderate OI
    Low    → low liquidity
    """
    if oi is None:
        if spread_pct >= 0.10:
            return "Medium"
        return "Low"

    if spread_pct >= 0.05 and oi >= 10_000_000:
        return "High"
    if spread_pct >= 0.02 and oi >= 2_000_000:
        return "Medium"
    return "Low"


def best_mark_price(entries: list[FundingRateEntry]) -> float | None:
    """Return the first available mark price from a list of entries."""
    for e in entries:
        if e.mark_price is not None and e.mark_price > 0:
            return e.mark_price
    return None


def best_oi(entries: list[FundingRateEntry]) -> float | None:
    """Return the maximum available OI value from a list of entries."""
    oi_values = [e.oi for e in entries if e.oi is not None and e.oi > 0]
    return max(oi_values) if oi_values else None


def earliest_next_funding(entries: list[FundingRateEntry]) -> int | None:
    """Return the nearest next funding timestamp across all entries."""
    times = [e.next_funding_time for e in entries if e.next_funding_time]
    return min(times) if times else None
