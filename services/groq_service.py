import logging
from groq import AsyncGroq
from config import GROQ_API_KEY, DEFAULT_MODEL

logger = logging.getLogger(__name__)

client = AsyncGroq(api_key=GROQ_API_KEY)


SYSTEM_PROMPTS = {
    "en": "You are a helpful assistant. Answer concisely in English.",
    "ru": "Ты полезный ассистент. Отвечай кратко на русском языке.",
    "uk": "Ти корисний асистент. Відповідай стисло українською мовою.",
}


async def ask_ai(user_message: str, lang: str = "en", model: str = None) -> str:
    """Отправляет вопрос в Groq. lang: 'en', 'ru', 'uk' — язык ответа."""
    system_prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["en"])

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
    # Whisper принимает ISO-639-1 коды
    whisper_lang = {"en": "en", "ru": "ru", "uk": "uk"}.get(lang, "en")

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
        raiseы