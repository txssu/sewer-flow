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

from src.attachment_storage import AttachmentStorage, InlineAttachmentStorage
from src.canonical import CanonicalUpdate, UserFrom, UserId
from src.providers.base import BaseProvider


class TelegramProvider(BaseProvider):
    """Telegram messaging provider using aiogram."""

    bot: Bot
    dispatcher: Dispatcher
    storage: AttachmentStorage

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
        self.storage = InlineAttachmentStorage()

        # Register message handler
        _ = self.dispatcher.message()(self._handle_message)

    async def _handle_message(self, message: Message) -> None:
        """Handle incoming Telegram message.

        Args:
            message: Incoming message from Telegram
        """
        if message.from_user is None:
            self.logger.warning("Received message with missing required fields")
            return

        text = message.text or message.caption

        user_id = UserId(type="telegram", value=str(message.from_user.id))
        user_from = UserFrom(
            fullname=message.from_user.full_name,
            username=message.from_user.username,
            language_code=message.from_user.language_code,
        )
        sent_at = message.date.isoformat()

        attachment = None
        file_id = None
        file_type = None
        if message.photo:
            file_id = message.photo[-1].file_id
            file_type = "photo"
        elif message.document:
            file_id = message.document.file_id
            file_type = "document"

        if file_id and file_type:
            file = await self.bot.get_file(file_id)
            if file.file_path:
                attachment = await self.storage.store(
                    file.file_path, file_type, self.bot
                )

        canonical_update = CanonicalUpdate(
            id=user_id,
            from_user=user_from,
            text=text,
            sent_at=sent_at,
            attachment=attachment,
        )

        await self.send_to_redis(canonical_update)
        self.logger.info(
            f"Sent message to {self.redis_stream} from user {user_id.value}"
        )

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
