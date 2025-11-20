import base64
import json
from dataclasses import dataclass
from os import getenv
from typing import TypedDict, cast


class BotConfigDict(TypedDict):
    """Type definition for bot configuration dictionary."""

    app: str
    platform: str
    token: str


class BotsConfigData(TypedDict):
    """Type definition for the config data structure."""

    bots: list[BotConfigDict]


@dataclass
class BotConfig:
    app: str
    platform: str
    token: str


def parse_config() -> list[BotConfig]:
    """Parse bot configuration from environment variables.

    Supports two methods (checked in order):
    1. SF_BOTS_CONFIG_PATH - path to JSON file with config
    2. SF_B64_BOTS_CONFIG - base64-encoded JSON config

    Config schema:
    {
        "bots": [
            {
                "app": "stream_name",
                "platform": "telegram",
                "token": "BOT_TOKEN"
            }
        ]
    }

    Returns:
        List of BotConfig objects

    Raises:
        ValueError: If no valid config source is found or config is invalid
    """
    config_data = None

    # Try loading from file path
    config_path = getenv("SF_BOTS_CONFIG_PATH")
    if config_path:
        try:
            with open(config_path, "r") as f:
                config_data = cast(BotsConfigData, json.load(f))
        except FileNotFoundError:
            raise ValueError(f"Config file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")

    # Try loading from base64-encoded config
    if not config_data:
        b64_config = getenv("SF_B64_BOTS_CONFIG")
        if b64_config:
            try:
                decoded = base64.b64decode(b64_config)
                config_data = cast(BotsConfigData, json.loads(decoded))
            except Exception as e:
                raise ValueError(f"Failed to decode base64 config: {e}")

    if not config_data:
        raise ValueError(
            "No config found. Set either SF_BOTS_CONFIG_PATH or SF_B64_BOTS_CONFIG"
        )

    # Validate and parse config
    if "bots" not in config_data:
        raise ValueError("Config must contain 'bots' field")

    if not isinstance(config_data["bots"], list):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise ValueError("'bots' field must be a list")

    configs: list[BotConfig] = []
    for bot in config_data["bots"]:
        if not isinstance(bot, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError(f"Invalid bot config: {bot}. Must be a dict")

        required_fields = ["app", "platform", "token"]
        for field in required_fields:
            if field not in bot:
                raise ValueError(f"Bot config missing required field '{field}': {bot}")

        # Type assertion after runtime validation
        configs.append(
            BotConfig(
                app=bot["app"],
                platform=bot["platform"],
                token=bot["token"],
            )
        )

    if not configs:
        raise ValueError("No bots configured")

    return configs
