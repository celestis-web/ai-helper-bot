import asyncio
import logging
import os
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

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

# === Настройки webhook ===
# На Render: WEBHOOK_HOST = https://твой-сервис.onrender.com
# Локально: WEBHOOK_HOST = http://localhost
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "http://localhost")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Веб-сервер слушает порт
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8080))


async def on_startup(bot: Bot):
    """Устанавливает webhook при старте."""
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    logger.info(f"✅ Webhook установлен: {WEBHOOK_URL}")


async def on_shutdown(bot: Bot):
    """Удаляет webhook при остановке."""
    await bot.delete_webhook()
    logger.info("❌ Webhook удалён")


async def health_check(request):
    """Эндпоинт для проверки живости (Render его пингует)."""
    return web.Response(text="OK")


async def main():
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

    # Роутеры (admin первым, потом voice, потом user)
    dp.include_router(admin.router)
    dp.include_router(voice.router)
    dp.include_router(user.router)

    # Настраиваем webhook
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Создаём aiohttp-приложение
    app = web.Application()

    # /health — для Render
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    # Webhook handler
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)

    # Настройка приложения
    setup_application(app, dp, bot=bot)

    logger.info(f"🚀 Бот запущен на порту {WEBAPP_PORT}")

    # Запуск веб-сервера
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()

    # Держим сервер запущенным
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")