import time
from typing import Callable

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse
from django.conf import settings


class RateLimitMiddleware:
    """Simple fixed-window rate limiting per IP.

    Limits anonymous users to `MAX_REQUESTS` per `WINDOW_SECONDS`.
    Authenticated users have a higher threshold.
    """

    MAX_REQUESTS_ANON = 60
    MAX_REQUESTS_AUTH = 240
    WINDOW_SECONDS = 60

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        client_ip = self._get_client_ip(request)
        key = f"rl:{client_ip}:{int(time.time() // self.WINDOW_SECONDS)}"
        max_requests = (
            self.MAX_REQUESTS_AUTH if request.user.is_authenticated else self.MAX_REQUESTS_ANON
        )

        count = cache.get(key, 0)
        if count >= max_requests:
            return HttpResponse('Too many requests, slow down.', status=429)
        cache.set(key, count + 1, timeout=self.WINDOW_SECONDS)
        return self.get_response(request)

    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        """
        Determine client IP address.

        In reverse-proxy environments (e.g., Vercel), `X-Forwarded-For` is the
        primary source of client IP. This behavior is configurable via
        `RATE_LIMIT_TRUST_X_FORWARDED_FOR` to avoid accidental spoofing in
        non-proxied deployments.
        """
        remote = request.META.get('REMOTE_ADDR', 'unknown')

        trust_xff = getattr(settings, "RATE_LIMIT_TRUST_X_FORWARDED_FOR", True)
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if trust_xff and forwarded:
            # Standard format is "client, proxy1, proxy2"; take the left-most.
            client_ip = forwarded.split(',')[0].strip()
            return client_ip or remote

        return remote


