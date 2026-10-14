import logging
from groq import AsyncGroq
from config import GROQ_API_KEY, DEFAULT_MODEL, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

client = AsyncGroq(api_key=GROQ_API_KEY)


async def ask_ai(user_message: str, model: str = None, system_prompt: str = None) -> str:
    """
    Отправляет вопрос в Groq и возвращает ответ.
    """
    try:
        response = await client.chat.completions.create(
            model=model or DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt or SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=1024,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq error: {type(e).__name__}: {e}")
        raise


async def transcribe_voice(file_path: str) -> str:
    """
    Транскрибирует голосовое сообщение через Groq Whisper.
    """
    try:
        with open(file_path, "rb") as f:
            response = await client.audio.transcriptions.create(
                file=("voice.ogg", f.read()),
                model="whisper-large-v3",
                language="en",
            )
        return response.text
    except Exception as e:
        logger.error(f"Whisper error: {type(e).__name__}: {e}")
        raise