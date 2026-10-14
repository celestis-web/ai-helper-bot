import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database import init_db
from handlers import user, admin, voice

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main():
    # Проверка токена
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден в .env!")
        return

    # Инициализация БД
    await init_db()
    logger.info("✅ База данных инициализирована")

    # Бот и диспетчер
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Подключаем роутеры (ВАЖНО: admin ПЕРВЫМ, потом voice, потом user)
    dp.include_router(admin.router)
    dp.include_router(voice.router)
    dp.include_router(user.router)

    logger.info("🚀 Бот запущен!")

    # Удаляем вебхуки (на всякий случай) и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")