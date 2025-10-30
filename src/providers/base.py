from abc import ABC, abstractmethod

from src.canonical import CanonicalUpdate
from redis import Redis


class BaseProvider(ABC):
    """Abstract base class for messaging providers."""

    stream_name: str
    token: str
    redis_client: "Redis[bytes]"
    redis_stream: str

    def __init__(self, stream_name: str, token: str, redis_client: "Redis[bytes]"):
        """Initialize provider.

        Args:
            stream_name: Redis stream name (will be prefixed with 'updates:')
            token: Provider-specific authentication token
            redis_client: Redis client instance
        """
        self.stream_name = stream_name
        self.token = token
        self.redis_client = redis_client
        self.redis_stream = f"updates:{stream_name}"

    @abstractmethod
    async def start(self) -> None:
        """Start the provider (begin polling/listening for messages)."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the provider (cleanup resources)."""
        pass

    def send_to_redis(self, update: CanonicalUpdate) -> None:
        """Send canonical update to Redis stream.

        Args:
            update: Canonical update to send
        """
        self.redis_client.xadd(self.redis_stream, {"data": update.to_json()})
