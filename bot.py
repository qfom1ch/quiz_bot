import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_data.config import BOT_TOKEN
from database.utils import create_db
from quiz_bot.handlers import other_handlers, user_handlers
from quiz_bot.main_menu import set_main_menu

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    bot: Bot = Bot(token=BOT_TOKEN,
                   parse_mode='HTML')
    dp: Dispatcher = Dispatcher()

    create_db()

    await set_main_menu(bot)

    dp.include_router(user_handlers.router)
    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
