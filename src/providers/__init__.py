from src.providers.base import BaseProvider
from src.providers.telegram import TelegramProvider
from src.providers.tamtam import TamTamProvider
from src.providers.max import MaxProvider
from redis.asyncio import Redis


def create_provider(
    stream_name: str, provider_name: str, token: str, redis_client: "Redis[bytes]"
) -> BaseProvider:
    """Factory function to create provider instances.

    Args:
        stream_name: Redis stream name
        provider_name: Name of the provider (telegram, tamtam, max)
        token: Provider-specific authentication token
        redis_client: Redis client instance

    Returns:
        Provider instance

    Raises:
        ValueError: If provider_name is not supported
    """
    providers = {
        "telegram": TelegramProvider,
        "tamtam": TamTamProvider,
        "max": MaxProvider,
    }

    provider_class = providers.get(provider_name.lower())
    if provider_class is None:
        raise ValueError(
            f"Unknown provider: {provider_name}. Supported providers: {', '.join(providers.keys())}"
        )

    return provider_class(stream_name, token, redis_client)


__all__ = [
    "create_provider",
    "BaseProvider",
    "TelegramProvider",
    "TamTamProvider",
    "MaxProvider",
]
