"""
In-memory TTL cache.  Thread-safe via asyncio-friendly design
(single-threaded event loop means no mutex needed for dict ops).
"""
import time
from typing import Any


class InMemoryCache:
    """Simple TTL-based in-memory cache."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        """Return cached value or None if missing / expired."""
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: float) -> None:
        """Store value with a TTL in seconds."""
        self._store[key] = (value, time.monotonic() + ttl)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


# Singleton instance shared across the application
cache = InMemoryCache()
