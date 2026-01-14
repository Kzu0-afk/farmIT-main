import time
from dataclasses import dataclass

from django.core.cache import cache


@dataclass(frozen=True)
class ThrottleResult:
    allowed: bool
    remaining: int
    reset_seconds: int


def check_throttle(key: str, limit: int, window_seconds: int) -> ThrottleResult:
    """Fixed-window throttle backed by Django cache.

    Notes:
    - Uses the configured Django cache backend. In serverless environments, a
      local-memory cache is best-effort (per-instance), but still reduces abuse.
    - Returns a simple result object so callers can respond with 429.
    """
    if limit <= 0 or window_seconds <= 0:
        return ThrottleResult(allowed=True, remaining=limit, reset_seconds=window_seconds)

    bucket = int(time.time() // window_seconds)
    cache_key = f"th:{key}:{bucket}"

    # Prefer atomic increment if supported.
    try:
        count = cache.incr(cache_key)
    except Exception:
        # If key doesn't exist (or backend doesn't support incr), initialize.
        existing = cache.get(cache_key)
        if existing is None:
            cache.add(cache_key, 1, timeout=window_seconds)
            count = 1
        else:
            count = int(existing) + 1
            cache.set(cache_key, count, timeout=window_seconds)

    allowed = count <= limit
    remaining = max(0, limit - count)
    reset_seconds = int(((bucket + 1) * window_seconds) - time.time())
    if reset_seconds < 0:
        reset_seconds = 0
    return ThrottleResult(allowed=allowed, remaining=remaining, reset_seconds=reset_seconds)


