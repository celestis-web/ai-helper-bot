from aiogram import Router, F
from aiogram.types import Message

from config import ADMIN_IDS, FREE_LIMIT
from database import (
    get_user, inc_questions, get_questions_left,
    log_message,
)
from services.i18n import t
from services.groq_service import ask_ai, transcribe_voice

router = Router()


@router.message(F.voice)
async def handle_voice(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        return

    lang = user[3] or "en"
    is_premium = bool(user[6])
    is_banned = bool(user[10])
    user_is_admin = user_id in ADMIN_IDS

    if is_banned:
        await message.answer(t("banned", lang))
        return

    if not user_is_admin and not is_premium:
        left = await get_questions_left(user_id)
        if left <= 0:
            await message.answer(
                t("limit_reached", lang, used=FREE_LIMIT, total=FREE_LIMIT)
            )
            return

    await message.bot.send_chat_action(message.chat.id, "typing")

    # Скачиваем голосовое
    file = await message.bot.get_file(message.voice.file_id)
    file_path = f"/tmp/{message.voice.file_id}.ogg"
    await message.bot.download_file(file.file_path, file_path)

    # Распознаём
    text = await transcribe_voice(file_path)

    if not text:
        await message.answer(t("voice_error", lang) if "voice_error" in dir(t) else "❌ Could not recognize voice. Try again.")
        return

    await message.answer(f"🎤 _{text}_", parse_mode="Markdown")
    await message.bot.send_chat_action(message.chat.id, "typing")

    # Проверка на погоду
    text_lower = text.lower()
    weather_keywords = ["weather", "погода", "погоду", "погод", "температура", "temperature"]
    is_weather_query = any(kw in text_lower for kw in weather_keywords)

    if is_weather_query:
        from services.weather_service import get_weather, format_weather
        from handlers.user import _extract_city
        city = _extract_city(text)

        if city:
            w = await get_weather(city)
            if w:
                await message.answer(format_weather(w, lang))
                if not user_is_admin and not is_premium:
                    await inc_questions(user_id)
                await log_message(user_id, text, f"[WEATHER] {city}", "voice_weather")
                return

    # Обычный AI-ответ
    try:
        answer = await ask_ai(text, user_id=user_id, lang=lang)
    except Exception:
        await message.answer(t("error_generic", lang))
        return

    await log_message(user_id, text, answer, "voice")

    if not user_is_admin and not is_premium:
        await inc_questions(user_id)
        left = await get_questions_left(user_id)
        answer += f"\n\n_{t('questions_left', lang, count=left)}_"

    await message.answer(answer, parse_mode="Markdown")