from dataclasses import dataclass
from os import getenv

CONFIGS_DELIMETER = ", "
PARAMS_DELIMETER = " "


@dataclass
class BotConfig:
    stream_name: str
    provider: str
    token: str


def parse_config() -> list[BotConfig]:
    """Parse CONFIG environment variable.

    Format: stream_name:provider:token,stream_name2:provider2:token2
    Example: client1:telegram:TOKEN1,client2:telegram:TOKEN2,client3:tamtam:TOKEN3

    Returns:
        List of BotConfig objects
    """
    config_str = getenv("CONFIG")
    if not config_str:
        raise ValueError("CONFIG environment variable is not set")

    configs: list[BotConfig] = []
    for bot_config in config_str.split(CONFIGS_DELIMETER):
        parts = bot_config.strip().split(PARAMS_DELIMETER)
        if len(parts) != 3:
            raise ValueError(
                f"Invalid config format: {bot_config}. Expected: stream_name:provider:token"
            )

        stream_name, provider, token = parts
        configs.append(
            BotConfig(stream_name=stream_name, provider=provider, token=token)
        )

    return configs
