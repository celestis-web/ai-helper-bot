import logging
from groq import AsyncGroq
from config import GROQ_API_KEY, DEFAULT_MODEL

logger = logging.getLogger(__name__)

client = AsyncGroq(api_key=GROQ_API_KEY)


async def ask_ai(user_message: str, lang: str = "en", model: str = None) -> str:
    """
    Отправляет вопрос в Groq.
    ИИ отвечает ВСЕГДА на языке сообщения пользователя.
    lang — резервный язык, если сообщение непонятно.
    """
    system_prompt = (
        "You are a helpful assistant. "
        "IMPORTANT: Always respond in the SAME LANGUAGE as the user's message. "
        "If the user writes in Russian — answer in Russian. "
        "If in Ukrainian — answer in Ukrainian. "
        "If in English — answer in English. "
        "Never mix languages. Be concise."
    )

    try:
        response = await client.chat.completions.create(
            model=model or DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq error: {type(e).__name__}: {e}")
        raise


async def transcribe_voice(file_path: str, lang: str = "en") -> str:
    """Транскрибирует голосовое через Groq Whisper."""
    # Whisper — на русский для русских, на украинский для украинских
    whisper_lang = {"en": "en", "ru": "ru", "uk": "uk"}.get(lang, "ru")

    try:
        with open(file_path, "rb") as f:
            response = await client.audio.transcriptions.create(
                file=("voice.ogg", f.read()),
                model="whisper-large-v3",
                language=whisper_lang,
            )
        return response.text
    except Exception as e:
        logger.error(f"Whisper error: {type(e).__name__}: {e}")
        raise