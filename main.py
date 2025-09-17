import asyncio
import logging

from aiogram import Bot, Dispatcher

from config.config import load_config
from database.database import db_init

logger = logging.getLogger(__name__)


async def main():
    config = load_config()
    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
    )
    logger.info("Starting bot")

    bot = Bot(token=config.bot.token)
    dp = Dispatcher()

    db: dict = db_init()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
