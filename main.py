import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message

import redis

from src.canonical import CanonicalUpdate

r = redis.Redis(host="localhost", port=6379, db=0)

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")
if TOKEN is None:
    raise ValueError("BOT_TOKEN environment variable is not set")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message()
async def echo_handler(message: Message) -> None:
    assert message.from_user is not None
    assert message.from_user.id is not None
    assert message.text is not None
    x = CanonicalUpdate("tg_" + str(message.from_user.id), message.text)
    r.xadd("updates", {"data": x.to_json()})


async def main() -> None:
    assert TOKEN is not None
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
