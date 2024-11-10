import asyncio
import logging
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database.schemas import create_db_engine
from handlers import common_handlers


async def on_startup(bot: Bot) -> None:
    logging.info("🚀 Бот запущен.")


async def main() -> None:
    dp = Dispatcher()
    dp.startup.register(on_startup)

    dp.include_router(common_handlers.router)

    dp["db_engine"] = create_db_engine(config.db_path)

    # Информация о системе и чате
    dp["system_info"] = {}
    dp["system_info"]["started_at"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    bot = Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging._nameToLevel[config.level])

    logFormatter = logging.Formatter(
        "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        datefmt="%d.%m.%YT%H:%M:%SZ%z",
    )
    fileHandler = logging.FileHandler("app.log", encoding="utf8")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)


    try:
        web_users = asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        logging.info("❎ Бот остановлен.")
