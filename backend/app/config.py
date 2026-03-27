"""
Global configuration loaded from environment variables / .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    APP_TITLE: str = "Funding Rate Arbitrage Dashboard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Cache
    CACHE_TTL_SECONDS: int = 10

    # HTTP client
    HTTP_TIMEOUT_SECONDS: float = 10.0

    # Binance
    BINANCE_FUTURES_URL: str = "https://fapi.binance.com/fapi/v1/premiumIndex"

    # Bybit
    BYBIT_TICKERS_URL: str = "https://api.bybit.com/v5/market/tickers"

    # OKX
    OKX_FUNDING_URL: str = "https://www.okx.com/api/v5/public/funding-rate"

    # Bitget
    BITGET_FUNDING_URL: str = "https://api.bitget.com/api/v2/mix/market/tickers"


settings = Settings()
