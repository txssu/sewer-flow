import logging
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.types import Message
from redis.asyncio import Redis
from typing_extensions import override

from src.canonical import CanonicalUpdate
from src.providers.base import BaseProvider


class TelegramProvider(BaseProvider):
    """Telegram messaging provider using aiogram."""

    bot: Bot
    dispatcher: Dispatcher

    logger: logging.Logger

    def __init__(
        self,
        stream_name: str,
        token: str,
        redis_client: "Redis[bytes]",
    ):
        """Initialize Telegram provider.

        Args:
            stream_name: Redis stream name
            token: Telegram bot token
            redis_client: Redis client instance
        """
        super().__init__(stream_name, token, redis_client)

        self.logger = logging.getLogger(f"TelegramProvider:{stream_name}")

        api_url = getenv("TELEGRAM_API_URL")

        # Create session with custom API URL if provided
        session = None
        if api_url:
            session = AiohttpSession(
                api=TelegramAPIServer(
                    base=f"{api_url}/bot{{token}}/{{method}}",
                    file=f"{api_url}/file/bot{{token}}/{{method}}",
                )
            )
            self.logger.info(f"Using custom Telegram API URL: {api_url}")

        self.bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            session=session,
        )
        self.dispatcher = Dispatcher()

        # Register message handler
        _ = self.dispatcher.message()(self._handle_message)

    async def _handle_message(self, message: Message) -> None:
        """Handle incoming Telegram message.

        Args:
            message: Incoming message from Telegram
        """
        if message.from_user is None or message.text is None:
            self.logger.warning("Received message with missing required fields")
            return

        user_id = f"tg_{message.from_user.id}"
        sent_at = message.date.isoformat()
        canonical_update = CanonicalUpdate(
            user_id=user_id, text=message.text, sent_at=sent_at
        )

        await self.send_to_redis(canonical_update)
        self.logger.info(f"Sent message to {self.redis_stream} from user {user_id}")

    @override
    async def start(self) -> None:
        """Start polling for Telegram updates."""
        self.logger.info(f"Starting Telegram provider for stream: {self.stream_name}")
        await self.dispatcher.start_polling(self.bot)

    @override
    async def stop(self) -> None:
        """Stop the Telegram bot."""
        self.logger.info(f"Stopping Telegram provider for stream: {self.stream_name}")
        await self.bot.session.close()
