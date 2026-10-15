import os
import aiohttp
from config import GROQ_API_KEY, DEFAULT_MODEL
from services.memory import get_history, add_message

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
WHISPER_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

SYSTEM_PROMPT = (
    "You are a helpful AI assistant inside a Telegram bot. "
    "IMPORTANT RULE: Always respond in the SAME LANGUAGE as the user's latest message. "
    "If the user writes in Russian — answer in Russian. "
    "If the user writes in Ukrainian — answer in Ukrainian. "
    "If the user writes in English — answer in English. "
    "Never mix languages. Never switch to English unless the user wrote in English. "
    "Remember the conversation context and refer to previous messages when relevant. "
    "Be concise, friendly and helpful. Use plain text, no markdown formatting."
)


async def ask_ai(prompt: str, user_id: int = None, lang: str = "en", model: str = None) -> str:
    model = model or DEFAULT_MODEL

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if user_id is not None:
        messages.extend(get_history(user_id))

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(GROQ_URL, headers=headers, json=payload, timeout=60) as resp:
                if resp.status != 200:
                    err = await resp.text()
                    print(f"[Groq] error {resp.status}: {err}")
                    return "⚠️ AI service error. Try again later."

                data = await resp.json()
                answer = data["choices"][0]["message"]["content"].strip()

                if user_id is not None:
                    add_message(user_id, "user", prompt)
                    add_message(user_id, "assistant", answer)

                return answer
    except Exception as e:
        print(f"[Groq] exception: {e}")
        return "⚠️ AI service error. Try again later."


async def transcribe_voice(file_path: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }

    try:
        async with aiohttp.ClientSession() as session:
            with open(file_path, "rb") as f:
                form = aiohttp.FormData()
                form.add_field("file", f, filename="voice.ogg", content_type="audio/ogg")
                form.add_field("model", "whisper-large-v3")
                form.add_field("response_format", "text")

                async with session.post(WHISPER_URL, headers=headers, data=form, timeout=120) as resp:
                    if resp.status != 200:
                        err = await resp.text()
                        print(f"[Whisper] error {resp.status}: {err}")
                        return ""
                    return (await resp.text()).strip()
    except Exception as e:
        print(f"[Whisper] exception: {e}")
        return ""