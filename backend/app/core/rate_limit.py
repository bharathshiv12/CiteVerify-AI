"""
In-memory rate limiter for zero-budget backend protection.
Provides per-client sliding window throttling on sensitive endpoints.
"""
import time
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import Request
from app.core.config import settings
from app.core.errors import RateLimitExceededError


class InMemoryRateLimiter:
    def __init__(self):
        # Maps key -> list of timestamp floats
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int, window_seconds: int = 60) -> Tuple[bool, int]:
        """
        Checks if request is allowed under sliding window.
        Returns (is_allowed, remaining_quota).
        """
        if not settings.RATE_LIMIT_ENABLED:
            return True, max_requests

        now = time.time()
        cutoff = now - window_seconds
        # Clean older entries
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]

        if len(self._requests[key]) >= max_requests:
            return False, 0

        self._requests[key].append(now)
        remaining = max_requests - len(self._requests[key])
        return True, remaining

    def check(self, request: Request, bucket: str, max_requests: int, window_seconds: int = 60):
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)
        key = f"{bucket}:{user_id or client_ip}"

        allowed, remaining = self.is_allowed(key, max_requests, window_seconds)
        if not allowed:
            raise RateLimitExceededError(
                message=f"Rate limit exceeded for {bucket}. Limit is {max_requests} requests per {window_seconds}s.",
                details={"bucket": bucket, "limit": max_requests, "window_seconds": window_seconds},
            )


limiter = InMemoryRateLimiter()
