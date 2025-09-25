import asyncio
import logging

from aiogram import Bot, Dispatcher

from config.config import load_config
from database.database import db_init
from keyboards.menu_commands import set_main_menu
from services.file_handling import prepare_book
from handlers.other import other_router
from handlers.user import user_router

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

    logger.info("Preparing book")
    book = prepare_book("book/book.txt")
    logger.info("The book is uploaded. Total pages: %d", len(book))

    db: dict = db_init()
    dp.workflow_data.update(book=book, db=db)

    await set_main_menu(bot)

    dp.include_router(user_router)
    dp.include_router(other_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
