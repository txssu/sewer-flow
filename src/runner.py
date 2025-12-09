import asyncio
import logging
import multiprocessing as mp
import os
import signal

from src.config import parse_config, BotConfig
from src.redis_client import get_redis_client
from src.providers import create_provider, BaseProvider


def _worker_process(
    worker_id: int,
    configs: list[BotConfig],
    log_level: int,
) -> None:
    """Worker process that runs providers in its own event loop.

    Args:
        worker_id: Worker process identifier
        configs: List of bot configurations for this worker
        log_level: Logging level to use
    """
    logging.basicConfig(level=log_level)
    logger = logging.getLogger(f"Worker-{worker_id}")

    logger.info(f"Worker {worker_id} starting with {len(configs)} provider(s)")

    # Each process creates its own Redis client
    redis_client = get_redis_client()

    providers: list[BaseProvider] = []
    for config in configs:
        try:
            provider = create_provider(
                stream_name=config.app,
                provider_name=config.platform,
                token=config.token,
                redis_client=redis_client,
            )
            providers.append(provider)
            logger.info(f"Created provider: {config.platform} for stream: {config.app}")
        except Exception as e:
            logger.error(
                f"Failed to create provider {config.platform} for stream {config.app}: {e}"
            )
            raise

    async def run_providers() -> None:
        """Run all providers concurrently in this process."""
        tasks = [provider.start() for provider in providers]
        try:
            _ = await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error running providers: {e}")
            raise
        finally:
            logger.info("Stopping providers")
            for provider in providers:
                try:
                    await provider.stop()
                except Exception as e:
                    logger.error(f"Error stopping provider: {e}")

    # Run event loop in this process
    asyncio.run(run_providers())


class MultiProviderRunner:
    """Runner for managing multiple messaging providers across processes."""

    logger: logging.Logger
    num_workers: int
    _processes: list[mp.Process]
    _configs: list[BotConfig]

    def __init__(self, num_workers: int | None = None):
        """Initialize the runner.

        Args:
            num_workers: Number of worker processes. Defaults to CPU count.
        """
        self._processes = []
        self._configs = []
        self.logger = logging.getLogger("MultiProviderRunner")
        self.num_workers = num_workers or os.cpu_count() or 1

    def initialize_providers(self) -> None:
        """Load provider configurations."""
        self._configs = parse_config()
        self.logger.info(f"Loaded {len(self._configs)} provider config(s)")

    def _distribute_configs(self) -> list[list[BotConfig]]:
        """Distribute configs evenly across workers.

        Returns:
            List of config lists, one per worker
        """
        num_workers = min(self.num_workers, len(self._configs))
        if num_workers == 0:
            return []

        distributed: list[list[BotConfig]] = [[] for _ in range(num_workers)]
        for i, config in enumerate(self._configs):
            distributed[i % num_workers].append(config)

        return distributed

    def run(self) -> None:
        """Run all providers across multiple processes."""
        if not self._configs:
            self.logger.error("No providers configured")
            return

        distributed = self._distribute_configs()
        actual_workers = len(distributed)

        self.logger.info(
            f"Starting {len(self._configs)} provider(s) across {actual_workers} process(es)"
        )

        log_level = logging.getLogger().level

        # Start worker processes
        for worker_id, worker_configs in enumerate(distributed):
            if not worker_configs:
                continue

            process = mp.Process(
                target=_worker_process,
                args=(worker_id, worker_configs, log_level),
                name=f"provider-worker-{worker_id}",
            )
            process.start()
            self._processes.append(process)
            self.logger.info(
                f"Started worker {worker_id} with {len(worker_configs)} provider(s)"
            )

        # Setup signal handlers for graceful shutdown
        def signal_handler(signum: int, _frame: object) -> None:
            self.logger.info(f"Received signal {signum}, stopping workers...")
            self.stop_all()

        _ = signal.signal(signal.SIGTERM, signal_handler)
        _ = signal.signal(signal.SIGINT, signal_handler)

        # Wait for all processes
        try:
            for process in self._processes:
                process.join()
        except KeyboardInterrupt:
            self.logger.info("Interrupted, stopping workers...")
            self.stop_all()

    def stop_all(self) -> None:
        """Stop all worker processes gracefully."""
        self.logger.info("Stopping all workers")

        for process in self._processes:
            if process.is_alive():
                process.terminate()

        # Wait for processes to terminate
        for process in self._processes:
            process.join(timeout=5)
            if process.is_alive():
                self.logger.warning(f"Force killing {process.name}")
                process.kill()

        self._processes.clear()
