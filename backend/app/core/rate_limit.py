from __future__ import annotations

from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, Request, status

_attempts: dict[str, deque[datetime]] = defaultdict(deque)


def check_login_rate_limit(
    request: Request, max_attempts: int = 10, window_seconds: int = 60
) -> None:
    key = request.client.host if request.client else "unknown"
    now = datetime.now(UTC)
    window = timedelta(seconds=window_seconds)
    attempts = _attempts[key]
    while attempts and now - attempts[0] > window:
        attempts.popleft()
    if len(attempts) >= max_attempts:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts"
        )
    attempts.append(now)
