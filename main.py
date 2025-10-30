import asyncio
import logging
import sys

from src.runner import MultiProviderRunner


async def main() -> None:
    """Main entry point."""
    runner = MultiProviderRunner()
    runner.initialize_providers()
    await runner.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
