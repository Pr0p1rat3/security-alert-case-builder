from __future__ import annotations

from redis import Redis
from rq import Queue

from app.core.config import get_settings


def get_redis() -> Redis:
    return Redis.from_url(get_settings().redis_url)


def get_default_queue() -> Queue:
    return Queue("default", connection=get_redis())
