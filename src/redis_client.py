from redis.asyncio import Redis
from os import getenv


def get_redis_client() -> "Redis[bytes]":
    """Get Redis client instance.

    Returns:
        Async Redis client configured from environment variables or defaults
    """
    host = getenv("SF_REDIS_HOST", "localhost")
    port = int(getenv("SF_REDIS_PORT", "6379"))
    db = int(getenv("SF_REDIS_DB", "0"))

    return Redis(host=host, port=port, db=db, decode_responses=False)
