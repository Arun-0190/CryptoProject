"""
Delta Exchange India funding rate service.
Endpoint: https://api.delta.exchange/v2/tickers

Delta returns ALL instruments in one flat list.
We only want:  contract_type == "perpetual_futures"
               symbol ends with USDT  (crypto pairs; excludes xStocks like NVDAXUSDT)
               funding_rate is not None
"""
from __future__ import annotations

import httpx

from app.config import settings
from app.models.response_models import FundingRateEntry
from app.utils.logger import get_logger
import time
from app.utils.debug import log_debug

logger = get_logger(__name__)

EXCHANGE = "Delta Exchange India"
URL = "https://api.delta.exchange/v2/tickers"

# Delta's funding interval is 8 h — same cadence as Binance, so rates are
# already per-8h.  We just need to convert from decimal fraction → %.
_CRYPTO_UNDERLYING_SYMBOLS = {
    "BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "ADA", "AVAX",
    "DOT", "LINK", "LTC", "MATIC", "UNI", "BCH", "ATOM",
    "NEAR", "APT", "OP", "ARB", "INJ", "SUI", "TRX",
}


def _is_crypto_perpetual(item: dict) -> bool:
    """
    Return True only for crypto USDT-settled perpetuals.
    Exclude xStock (equity) perpetuals like TSLAXUSDT, NVDAXUSDT.
    """
    if item.get("contract_type") != "perpetual_futures":
        return False
    symbol: str = item.get("symbol", "")
    if not symbol.endswith("USDT"):
        return False
    # Underlying asset must be a crypto (not an equity ticker)
    underlying: str = item.get("underlying_asset_symbol", "")
    if underlying and underlying not in _CRYPTO_UNDERLYING_SYMBOLS:
        return False
    raw_rate = item.get("funding_rate")
    if raw_rate is None:
        return False
    return True


def _to_percent(rate: float) -> float:
    """
    Delta reports funding_rate as a decimal fraction (e.g. -0.007857...).
    Convert to percentage:  -0.00786  →  -0.786 %
    If the value is somehow already large (|rate| >= 1) keep it as-is.
    """
    if abs(rate) < 1:
        return rate * 100
    return rate


async def fetch_delta_rates(client: httpx.AsyncClient) -> list[FundingRateEntry]:
    """Fetch and normalise Delta Exchange India USDT perpetual funding rates."""
    start_t = time.perf_counter()
    status_code = "UNKNOWN"
    errors = None
    payload: dict = {}
    raw: list[dict] = []
    
    try:
        resp = await client.get(URL, timeout=settings.HTTP_TIMEOUT_SECONDS)
        status_code = resp.status_code
        resp.raise_for_status()
        payload = resp.json()
        raw = payload.get("result", [])
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        errors = f"HTTP Error {status_code}: {exc}"
        logger.error("[%s] HTTP error %s: %s", EXCHANGE, status_code, exc)
    except Exception as exc:
        errors = f"Request Failed: {exc}"
        logger.error("[%s] Request failed: %s", EXCHANGE, exc)

    latency = (time.perf_counter() - start_t) * 1000
    results: list[FundingRateEntry] = []
    missing_fields: list[str] = []

    for item in raw:
        try:
            if not _is_crypto_perpetual(item):
                continue

            symbol: str = item["symbol"]  # already BTCUSDT format
            rate_raw = float(item["funding_rate"])
            funding_rate_pct = _to_percent(rate_raw)

            mark_price_raw = item.get("mark_price")
            mark_price = float(mark_price_raw) if mark_price_raw else None

            oi_raw = item.get("oi_value_usd")
            oi = float(oi_raw) if oi_raw else None

            results.append(
                FundingRateEntry(
                    symbol=symbol,
                    exchange=EXCHANGE,
                    funding_rate=round(funding_rate_pct, 6),
                    next_funding_time=None,  # Delta tickers don't expose next funding time
                    mark_price=mark_price,
                    oi=oi,
                )
            )
        except (KeyError, ValueError, TypeError) as exc:
            missing_fields.append(f"malformed: {exc}")
            logger.warning("[%s] Skipped malformed record: %s | %s", EXCHANGE, item.get("symbol"), exc)

    log_debug(
        exchange=EXCHANGE,
        endpoint=URL,
        latency_ms=latency,
        status_code=status_code,
        raw_response=payload,
        parsed_count=len(results),
        missing_fields=missing_fields,
        errors=errors
    )

    logger.info("[%s] Fetched %d crypto perpetuals", EXCHANGE, len(results))
    return results
