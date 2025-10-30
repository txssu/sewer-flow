from redis import Redis
from os import getenv


def get_redis_client() -> "Redis[bytes]":
    """Get Redis client instance.

    Returns:
        Redis client configured from environment variables or defaults
    """
    host = getenv("REDIS_HOST", "localhost")
    port = int(getenv("REDIS_PORT", "6379"))
    db = int(getenv("REDIS_DB", "0"))

    return Redis(host=host, port=port, db=db, decode_responses=False)
