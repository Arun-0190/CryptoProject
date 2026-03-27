"""
Pydantic response models for the API.
"""
from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel


class FundingRateEntry(BaseModel):
    """Normalised funding rate record from a single exchange."""

    symbol: str
    exchange: str
    funding_rate: float          # expressed in % (e.g. 0.01 = 0.01 %)
    next_funding_time: Optional[int] = None   # Unix ms
    mark_price: Optional[float] = None
    oi: Optional[float] = None   # Open Interest in USD (if available)


class ArbitrageOpportunity(BaseModel):
    """A single arbitrage opportunity across two exchanges."""

    symbol: str
    long_exchange: str
    short_exchange: str
    long_rate: float             # funding rate (%) – go long here (lowest)
    short_rate: float            # funding rate (%) – go short here (highest)
    funding_diff: float          # spread = short_rate − long_rate
    apr: float                   # annualised percentage return
    mark_price: Optional[float] = None
    oi: Optional[float] = None
    next_funding_time: Optional[int] = None
    confidence: Literal["High", "Medium", "Low"]
    risk: Literal["Low", "Medium", "High"]


class ArbitrageResponse(BaseModel):
    """Top-level API response."""

    success: bool
    timestamp: int
    count: int
    data: list[ArbitrageOpportunity]


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
