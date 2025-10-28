import base64
from abc import ABC, abstractmethod
from io import BytesIO

from aiogram import Bot
from typing_extensions import override

from src.canonical import Attachment


class AttachmentStorage(ABC):
    """Abstract interface for storing message attachments."""

    @abstractmethod
    async def store(self, file_path: str, file_type: str, bot: Bot) -> Attachment:
        """Download and store an attachment.

        Args:
            file_path: Telegram file path obtained from bot.get_file()
            file_type: General file type (e.g. "photo", "document")
            bot: aiogram Bot instance for downloading
        """


class InlineAttachmentStorage(AttachmentStorage):
    """Stores attachment content inline as a base64-encoded string."""

    @override
    async def store(self, file_path: str, file_type: str, bot: Bot) -> Attachment:
        buffer = BytesIO()
        _ = await bot.download_file(file_path, buffer)
        data = base64.b64encode(buffer.getvalue()).decode()
        return Attachment(type=file_type, encoding="base64", data=data)
