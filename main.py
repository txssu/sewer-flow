import logging
import sys

from src.runner import MultiProviderRunner


def main() -> None:
    """Main entry point."""
    runner = MultiProviderRunner()
    runner.initialize_providers()
    runner.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
