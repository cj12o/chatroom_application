import redis
from django.conf import settings
from base.logger import logger

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(settings.REDIS_URL)
    return _redis_client


def check_and_increment(user_id: int, service: str) -> bool:
    """
    Check if a user has remaining LLM calls for a service within the time window.
    Returns True if the call is allowed, False if rate-limited.

    Keys are per-user, per-service with a TTL window.
    Example key: "ratelimit:llm:3:recommendation"
    """
    limit_config = settings.LLM_RATE_LIMITS.get(service)
    if limit_config is None:
        return True  # no limit configured for this service

    max_calls = limit_config["max_calls"]
    window_seconds = limit_config["window"]

    key = f"ratelimit:llm:{user_id}:{service}"
    r = _get_redis()

    current = r.get(key)
    if current is not None and int(current) >= max_calls:
        logger.warning(f"Rate limit hit: user={user_id} service={service} limit={max_calls}/{window_seconds}s")
        return False

    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, window_seconds)
    pipe.execute()
    return True


def get_remaining(user_id: int, service: str) -> int:
    """Return how many LLM calls a user has left for a service."""
    limit_config = settings.LLM_RATE_LIMITS.get(service)
    if limit_config is None:
        return -1  # unlimited

    max_calls = limit_config["max_calls"]
    key = f"ratelimit:llm:{user_id}:{service}"
    r = _get_redis()
    current = r.get(key)
    used = int(current) if current else 0
    return max(0, max_calls - used)
