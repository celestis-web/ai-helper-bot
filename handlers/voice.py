import os
import tempfile
import logging

from aiogram import Router, F
from aiogram.types import Message

from config import ADMIN_ID, FREE_LIMIT
from database import (
    get_user, inc_questions, get_questions_left, log_message,
)
from services.i18n import t
from services.groq_service import ask_ai, transcribe_voice

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.voice)
async def handle_voice(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        return

    lang = user[3] or "en"
    is_premium = bool(user[6])
    is_banned = bool(user[10])
    is_admin = user_id == ADMIN_ID

    if is_banned:
        await message.answer(t("banned", lang))
        return

    # Проверка лимита
    if not is_admin and not is_premium:
        left = await get_questions_left(user_id)
        if left <= 0:
            await message.answer(
                t("limit_reached", lang, used=FREE_LIMIT, total=FREE_LIMIT)
            )
            return

    # Сообщаем что обрабатываем
    processing_msg = await message.answer(t("voice_processing", lang))

    # Скачиваем голосовое
    file = await message.bot.get_file(message.voice.file_id)
    tmp_path = os.path.join(tempfile.gettempdir(), f"voice_{user_id}.ogg")
    await message.bot.download_file(file.file_path, tmp_path)

    # Транскрибируем
    try:
        transcribed_text = await transcribe_voice(tmp_path)
    except Exception as e:
        logger.error(f"Voice transcribe error: {e}")
        await processing_msg.edit_text(t("voice_error", lang))
        return
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    if not transcribed_text or not transcribed_text.strip():
        await processing_msg.edit_text(t("voice_error", lang))
        return

    # Показываем расшифровку
    await processing_msg.edit_text(f"🎙 _{transcribed_text}_", parse_mode="Markdown")

    # === Проверка: не просит ли юзер погоду ===
    text_lower = transcribed_text.lower()
    weather_keywords = ["weather", "погода", "погоду", "погод", "температура", "temperature"]
    is_weather_query = any(kw in text_lower for kw in weather_keywords)

    if is_weather_query:
        from services.weather_service import get_weather, format_weather
        from handlers.user import _extract_city

        city = _extract_city(transcribed_text)

        if city:
            w = await get_weather(city)
            if w:
                await message.answer(format_weather(w, lang))
                if not is_admin and not is_premium:
                    await inc_questions(user_id)
                await log_message(user_id, f"[VOICE+WEATHER] {transcribed_text}", f"[WEATHER] {city}", "weather")
                return
            else:
                await message.answer(
                    f"❌ Could not find city: {city}\nTry again with a different name."
                )
                return

    # === Обычный запрос к ИИ ===
    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        answer = await ask_ai(transcribed_text)
    except Exception as e:
        logger.error(f"Groq error: {e}")
        await message.answer(t("error_generic", lang))
        return

    await log_message(user_id, f"[VOICE] {transcribed_text}", answer, "whisper+gpt")

    if not is_admin and not is_premium:
        await inc_questions(user_id)
        left = await get_questions_left(user_id)
        answer += f"\n\n_{t('questions_left', lang, count=left)}_"

    await message.answer(answer, parse_mode="Markdown")