from typing_extensions import override

from redis import Redis

from src.providers.base import BaseProvider


class MaxProvider(BaseProvider):
    """Max messaging provider (stub for future implementation)."""

    def __init__(self, stream_name: str, token: str, redis_client: "Redis[bytes]"):
        """Initialize Max provider.

        Args:
            stream_name: Redis stream name
            token: Max bot token
            redis_client: Redis client instance
        """
        super().__init__(stream_name, token, redis_client)

    @override
    async def start(self) -> None:
        """Start Max provider."""
        raise NotImplementedError("Max provider is not implemented yet")

    @override
    async def stop(self) -> None:
        """Stop Max provider."""
        raise NotImplementedError("Max provider is not implemented yet")
