import time
from typing import Callable

from django.core.cache import cache
from django.http import HttpRequest, HttpResponse


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
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


