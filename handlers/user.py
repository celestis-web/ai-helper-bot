from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery

from config import ADMIN_ID, FREE_LIMIT, PREMIUM_PRICE_STARS
from database import (
    add_user, get_user, inc_questions, get_questions_left,
    set_language, get_language, log_message, set_premium, add_payment,
)
from keyboards.user_kb import (
    main_menu_kb, language_kb, back_to_menu_kb,
    buy_premium_kb, referral_kb, profile_kb,
)
from services.i18n import t
from services.referral_service import parse_referral_param
from services.groq_service import ask_ai
from services.memory import clear_history

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    args = message.text.split(maxsplit=1)
    start_param = args[1] if len(args) > 1 else None
    referrer_id = parse_referral_param(start_param) if start_param else None

    user_id = message.from_user.id

    if referrer_id == user_id:
        referrer_id = None

    existing_user = await get_user(user_id)
    is_new_user = existing_user is None

    await add_user(
        user_id=user_id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        referrer_id=referrer_id,
    )

    if is_new_user and referrer_id:
        from handlers.referral import notify_referrer
        await notify_referrer(
            message.bot,
            referrer_id,
            message.from_user.first_name or "friend",
        )

    user = await get_user(user_id)
    is_premium = bool(user[6]) if user else False
    lang = user[3] if user else "en"

    await message.answer(
        f"Hi, {message.from_user.first_name or 'friend'}! 👋\n\n"
        f"I'm an AI-powered assistant. Ask me anything — I'll reply in seconds.\n\n"
        f"(Change language anytime via 🌍 button)",
        reply_markup=main_menu_kb(lang, is_premium),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    lang = await get_language(message.from_user.id)
    user = await get_user(message.from_user.id)
    is_premium = bool(user[6]) if user else False

    await message.answer(
        t("menu", lang),
        reply_markup=main_menu_kb(lang, is_premium),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    lang = await get_language(message.from_user.id)
    await message.answer(
        t("menu", lang),
        reply_markup=main_menu_kb(lang),
    )


@router.message(Command("reset"))
async def cmd_reset(message: Message):
    clear_history(message.from_user.id)
    lang = await get_language(message.from_user.id)
    texts = {
        "en": "🧹 Context cleared. Starting fresh.",
        "ru": "🧹 Контекст очищен. Начинаем с чистого листа.",
        "uk": "🧹 Контекст очищено. Починаємо з чистого аркуша.",
    }
    await message.answer(texts.get(lang, texts["en"]))


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        lang = await get_language(message.from_user.id)
        await message.answer(t("admin_only", lang))
        return

    from keyboards.admin_kb import admin_menu_kb
    await message.answer(
        t("admin_menu", "en"),
        reply_markup=admin_menu_kb(),
    )


@router.callback_query(F.data.startswith("lang_"))
async def cb_set_language(callback: CallbackQuery):
    lang = callback.data.split("_")[1]
    await set_language(callback.from_user.id, lang)

    user = await get_user(callback.from_user.id)
    is_premium = bool(user[6]) if user else False

    await callback.message.edit_text(
        t("language_set", lang) + "\n\n" + t("menu", lang),
        reply_markup=main_menu_kb(lang, is_premium),
    )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery):
    lang = await get_language(callback.from_user.id)
    user = await get_user(callback.from_user.id)
    is_premium = bool(user[6]) if user else False

    await callback.message.edit_text(
        t("menu", lang),
        reply_markup=main_menu_kb(lang, is_premium),
    )
    await callback.answer()


@router.callback_query(F.data == "change_lang")
async def cb_change_lang(callback: CallbackQuery):
    lang = await get_language(callback.from_user.id)
    await callback.message.edit_text(
        t("choose_language", lang),
        reply_markup=language_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "profile")
async def cb_profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_language(user_id)
    user = await get_user(user_id)

    if not user:
        await callback.answer("Error", show_alert=True)
        return

    used = user[4]
    referrals = user[9]
    is_premium = bool(user[6])
    status = t("status_premium", lang) if is_premium else t("status_free", lang)

    text = (
        f"{t('profile_title', lang)}\n\n"
        f"{t('profile_id', lang, user_id=user_id)}\n"
        f"{t('profile_used', lang, used=used)}\n"
        f"{t('profile_referrals', lang, count=referrals)}\n"
        f"{t('profile_status', lang, status=status)}"
    )

    await callback.message.edit_text(text, reply_markup=profile_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "referral")
async def cb_referral(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_language(user_id)

    bot_info = await callback.bot.get_me()
    user = await get_user(user_id)
    referrals = user[9] if user else 0

    text = (
        f"{t('referral_title', lang)}\n\n"
        f"{t('referral_desc', lang)}\n"
        f"`https://t.me/{bot_info.username}?start=ref_{user_id}`\n\n"
        f"🎁 Friends: {referrals}"
    )

    await callback.message.edit_text(
        text,
        reply_markup=referral_kb(bot_info.username, user_id, lang),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def cb_help(callback: CallbackQuery):
    lang = await get_language(callback.from_user.id)
    text = {
        "en": "💬 Just send me a message and I'll reply.\n\nCommands:\n/menu — menu\n/reset — clear context\n/admin — admin (owner only)",
        "ru": "💬 Просто напиши мне сообщение — я отвечу.\n\nКоманды:\n/menu — меню\n/reset — очистить контекст\n/admin — админка (только владелец)",
        "uk": "💬 Просто надішли мені повідомлення — я відповім.\n\nКоманди:\n/menu — меню\n/reset — очистити контекст\n/admin — адмінка (тільки власник)",
    }
    await callback.message.edit_text(text.get(lang, text["en"]), reply_markup=back_to_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "buy_premium")
async def cb_buy_premium(callback: CallbackQuery):
    lang = await get_language(callback.from_user.id)
    await callback.message.edit_text(
        t("premium_title", lang) + "\n\n" + t("premium_desc", lang, price=PREMIUM_PRICE_STARS),
        reply_markup=buy_premium_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "pay_premium")
async def cb_pay_premium(callback: CallbackQuery):
    try:
        await callback.message.answer_invoice(
            title="Premium Access",
            description="Unlimited questions for 30 days",
            payload=f"premium_{callback.from_user.id}",
            currency="XTR",
            prices=[LabeledPrice(label="Premium", amount=PREMIUM_PRICE_STARS)],
            provider_token="",
        )
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Error: {e}", show_alert=True)


@router.pre_checkout_query()
async def process_pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(message: Message):
    user_id = message.from_user.id
    payment = message.successful_payment

    await set_premium(user_id, days=30)
    await add_payment(
        user_id=user_id,
        amount=payment.total_amount,
        currency=payment.currency,
        payload=payment.invoice_payload,
        tg_payment_id=payment.telegram_payment_charge_id,
    )

    lang = await get_language(user_id)
    await message.answer(t("premium_paid", lang))

    try:
        await message.bot.send_message(
            ADMIN_ID,
            f"💰 New payment!\n\n"
            f"User: {user_id}\n"
            f"Amount: {payment.total_amount} ⭐\n"
            f"Charge ID: {payment.telegram_payment_charge_id}"
        )
    except Exception:
        pass


@router.callback_query(F.data == "premium_info")
async def cb_premium_info(callback: CallbackQuery):
    lang = await get_language(callback.from_user.id)
    user = await get_user(callback.from_user.id)
    until = user[7] if user else None
    text = t("premium_until", lang, date=until or "—")
    await callback.message.edit_text(text, reply_markup=back_to_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == "ask_ai")
async def cb_ask_ai(callback: CallbackQuery):
    lang = await get_language(callback.from_user.id)
    text = {
        "en": "💬 Just send your question as a message.",
        "ru": "💬 Просто отправь свой вопрос сообщением.",
        "uk": "💬 Просто надішли своє питання повідомленням.",
    }
    await callback.message.edit_text(text.get(lang, text["en"]), reply_markup=back_to_menu_kb(lang))
    await callback.answer()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message):
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

    if not is_admin and not is_premium:
        left = await get_questions_left(user_id)
        if left <= 0:
            await message.answer(
                t("limit_reached", lang, used=FREE_LIMIT, total=FREE_LIMIT)
            )
            return

    await message.bot.send_chat_action(message.chat.id, "typing")

    text_lower = message.text.lower()
    weather_keywords = ["weather", "погода", "погоду", "погод", "температура", "temperature"]
    is_weather_query = any(kw in text_lower for kw in weather_keywords)

    if is_weather_query:
        from services.weather_service import get_weather, format_weather
        city = _extract_city(message.text)

        if city:
            w = await get_weather(city)
            if w:
                await message.answer(format_weather(w, lang))
                if not is_admin and not is_premium:
                    await inc_questions(user_id)
                await log_message(user_id, message.text, f"[WEATHER] {city}", "weather")
                return
            else:
                await message.answer(
                    f"❌ Could not find city: {city}\nTry again with a different name."
                )
                return

    try:
        answer = await ask_ai(message.text, user_id=user_id, lang=lang)
    except Exception:
        await message.answer(t("error_generic", lang))
        return

    await log_message(user_id, message.text, answer, "default")

    if not is_admin and not is_premium:
        await inc_questions(user_id)
        left = await get_questions_left(user_id)
        answer += f"\n\n_{t('questions_left', lang, count=left)}_"

    await message.answer(answer, parse_mode="Markdown")


def _extract_city(text: str) -> str | None:
    import re

    cleaned = text.lower()

    phrases = [
        "what's the weather in", "what is the weather in",
        "what's the weather like in", "what is the weather like in",
        "what's the weather", "what is the weather",
        "how's the weather in", "how is the weather in",
        "how's the weather", "how is the weather",
        "weather forecast for", "weather forecast in",
        "weather in", "weather for", "weather at",
        "weather",
        "погода в", "погода у", "погода на", "погода",
        "погоду в", "погоду у", "погоду",
        "какая погода в", "какая погода у", "какая погода",
        "температура в", "температура у", "температура",
        "temperature in", "temperature for", "temperature",
    ]
    for phrase in phrases:
        cleaned = cleaned.replace(phrase, "")

    cleaned = re.sub(r"[?.!,;:'\"]", "", cleaned).strip()

    if not cleaned:
        return None

    words = cleaned.split()
    if not words:
        return None

    stop_words = {
        "what", "whats", "how", "hows", "is", "the", "a", "an",
        "please", "tell", "me", "today", "now", "current",
        "какая", "какой", "как", "что", "сейчас", "сегодня",
        "расскажи", "скажи", "мне",
    }

    while words and words[0] in stop_words:
        words.pop(0)

    if not words:
        return None

    if len(words) >= 2 and words[0] in ["new", "san", "los", "saint", "st", "las", "буэнос"]:
        return f"{words[0].title()} {words[1].title()}"

    return words[0].title()