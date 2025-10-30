import asyncio
import logging

from src.config import parse_config
from src.redis_client import get_redis_client
from src.providers import create_provider, BaseProvider


class MultiProviderRunner:
    """Runner for managing multiple messaging providers."""

    providers: list[BaseProvider]
    logger: logging.Logger

    def __init__(self):
        """Initialize the runner."""
        self.providers = []
        self.logger = logging.getLogger("MultiProviderRunner")

    def initialize_providers(self) -> None:
        """Initialize all providers from config."""
        configs = parse_config()
        redis_client = get_redis_client()

        self.logger.info(f"Initializing {len(configs)} provider(s)")

        for config in configs:
            try:
                provider = create_provider(
                    stream_name=config.stream_name,
                    provider_name=config.provider,
                    token=config.token,
                    redis_client=redis_client,
                )
                self.providers.append(provider)
                self.logger.info(
                    f"Created provider: {config.provider} for stream: {config.stream_name}"
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to create provider {config.provider} for stream {config.stream_name}: {e}"
                )
                raise

    async def run(self) -> None:
        """Run all providers concurrently."""
        if not self.providers:
            self.logger.error("No providers initialized")
            return

        self.logger.info(f"Starting {len(self.providers)} provider(s)")

        # Run all providers concurrently
        tasks = [provider.start() for provider in self.providers]

        try:
            _ = await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Error running providers: {e}")
            raise
        finally:
            await self.stop_all()

    async def stop_all(self) -> None:
        """Stop all providers gracefully."""
        self.logger.info("Stopping all providers")

        for provider in self.providers:
            try:
                await provider.stop()
            except Exception as e:
                self.logger.error(f"Error stopping provider: {e}")
