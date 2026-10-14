import os
from dotenv import load_dotenv

load_dotenv()

# === Основное ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8794296833"))

# === Лимиты ===
FREE_LIMIT = 10
REFERRAL_BONUS = 5          # +5 вопросов за друга
REFERRAL_PREMIUM_THRESHOLD = 10  # 10 друзей = премиум

# === Оплата ===
PREMIUM_PRICE_STARS = 100   # цена премиума в Stars

# === ИИ ===
DEFAULT_MODEL = "openai/gpt-oss-120b"
SYSTEM_PROMPT = "You are a helpful assistant. Answer concisely and to the point in English."

# === БД ===
DB_PATH = "bot.db"
DB_URL = os.getenv("DATABASE_URL", "")