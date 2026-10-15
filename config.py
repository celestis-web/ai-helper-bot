import os
from dotenv import load_dotenv

load_dotenv()

# === Основное ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Главный админ (всегда админ)
ADMIN_ID = int(os.getenv("ADMIN_ID", "8794296833"))

# Дополнительные админы через запятую в env: ADMIN_IDS="123,456,789"
_extra_ids_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [ADMIN_ID] + [
    int(x.strip()) for x in _extra_ids_raw.split(",") if x.strip().isdigit()
]


def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь админом."""
    return user_id in ADMIN_IDS


# === Лимиты ===
FREE_LIMIT = 10
REFERRAL_BONUS = 5
REFERRAL_PREMIUM_THRESHOLD = 10

# === Оплата ===
PREMIUM_PRICE_STARS = 100

# === ИИ ===
DEFAULT_MODEL = "openai/gpt-oss-120b"
SYSTEM_PROMPT = "You are a helpful assistant. Answer concisely and to the point in English."

# === БД ===
DB_PATH = "bot.db"
DB_URL = os.getenv("DATABASE_URL", "")