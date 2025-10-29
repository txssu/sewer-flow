import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")
if TOKEN is None:
    raise ValueError("BOT_TOKEN environment variable is not set")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message()
async def echo_handler(message: Message) -> None:
    print(message.text)


async def main() -> None:
    assert TOKEN is not None
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
