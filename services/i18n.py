"""
Простая локализация. Три языка: en, ru, uk.
"""

LANGUAGES = {
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
    "uk": "🇺🇦 Українська",
}

DEFAULT_LANG = "en"


TRANSLATIONS = {
    # === START ===
    "welcome": {
        "en": "Hi, {name}! 👋\n\nI'm an AI assistant. Ask me anything and I'll reply.",
        "ru": "Привет, {name}! 👋\n\nЯ — AI-помощник. Задай вопрос, и я отвечу.",
        "uk": "Привіт, {name}! 👋\n\nЯ — AI-помічник. Задай питання, і я відповім.",
    },
    "choose_language": {
        "en": "🌍 Choose your language:",
        "ru": "🌍 Выбери язык:",
        "uk": "🌍 Обери мову:",
    },
    "language_set": {
        "en": "✅ Language set to English",
        "ru": "✅ Язык изменён на русский",
        "uk": "✅ Мову змінено на українську",
    },

    # === MENU ===
    "menu": {
        "en": "Main menu:",
        "ru": "Главное меню:",
        "uk": "Головне меню:",
    },
    "btn_ask_ai": {
        "en": "💬 Ask AI",
        "ru": "💬 Спросить AI",
        "uk": "💬 Запитати AI",
    },
    "btn_profile": {
        "en": "👤 Profile",
        "ru": "👤 Профиль",
        "uk": "👤 Профіль",
    },
    "btn_referral": {
        "en": "🎁 Referral",
        "ru": "🎁 Рефералы",
        "uk": "🎁 Реферали",
    },
    "btn_buy_premium": {
        "en": "💎 Buy Premium",
        "ru": "💎 Купить Премиум",
        "uk": "💎 Купити Преміум",
    },
    "btn_premium_active": {
        "en": "👑 Premium Active",
        "ru": "👑 Премиум Активен",
        "uk": "👑 Преміум Активний",
    },
    "btn_help": {
        "en": "ℹ️ Help",
        "ru": "ℹ️ Помощь",
        "uk": "ℹ️ Допомога",
    },
    "btn_back": {
        "en": "⬅️ Back",
        "ru": "⬅️ Назад",
        "uk": "⬅️ Назад",
    },
    "btn_change_lang": {
        "en": "🌍 Change language",
        "ru": "🌍 Сменить язык",
        "uk": "🌍 Змінити мову",
    },

    # === STATUS ===
    "questions_left": {
        "en": "🆓 Free questions left: {count}",
        "ru": "🆓 Бесплатных вопросов осталось: {count}",
        "uk": "🆓 Безкоштовних питань залишилось: {count}",
    },
    "premium_status": {
        "en": "👑 Premium active",
        "ru": "👑 Премиум активен",
        "uk": "👑 Преміум активний",
    },
    "premium_until": {
        "en": "👑 Premium until: {date}",
        "ru": "👑 Премиум до: {date}",
        "uk": "👑 Преміум до: {date}",
    },
    "limit_reached": {
        "en": "🚫 Free questions used up ({used}/{total}).\n\nBuy premium: /buy",
        "ru": "🚫 Бесплатные вопросы закончились ({used}/{total}).\n\nКупи премиум: /buy",
        "uk": "🚫 Безкоштовні питання закінчились ({used}/{total}).\n\nКупи преміум: /buy",
    },

    # === PROFILE ===
    "profile_title": {
        "en": "👤 Your profile",
        "ru": "👤 Твой профиль",
        "uk": "👤 Твій профіль",
    },
    "profile_id": {
        "en": "🆔 ID: {user_id}",
        "ru": "🆔 ID: {user_id}",
        "uk": "🆔 ID: {user_id}",
    },
    "profile_used": {
        "en": "❓ Questions used: {used}",
        "ru": "❓ Вопросов задано: {used}",
        "uk": "❓ Питань задано: {used}",
    },
    "profile_referrals": {
        "en": "🎁 Invited friends: {count}",
        "ru": "🎁 Приглашено друзей: {count}",
        "uk": "🎁 Запрошено друзів: {count}",
    },
    "profile_status": {
        "en": "📊 Status: {status}",
        "ru": "📊 Статус: {status}",
        "uk": "📊 Статус: {status}",
    },
    "status_premium": {
        "en": "👑 Premium",
        "ru": "👑 Премиум",
        "uk": "👑 Преміум",
    },
    "status_free": {
        "en": "🆓 Free",
        "ru": "🆓 Бесплатный",
        "uk": "🆓 Безкоштовний",
    },

    # === REFERRAL ===
    "referral_title": {
        "en": "🎁 Referral system",
        "ru": "🎁 Реферальная система",
        "uk": "🎁 Реферальна система",
    },
    "referral_desc": {
        "en": (
            "Invite friends and get bonuses!\n\n"
            "• +5 free questions per friend\n"
            "• 10 friends = 1 month premium FREE\n\n"
            "Your link:"
        ),
        "ru": (
            "Приглашай друзей и получай бонусы!\n\n"
            "• +5 бесплатных вопросов за друга\n"
            "• 10 друзей = 1 месяц премиума БЕСПЛАТНО\n\n"
            "Твоя ссылка:"
        ),
        "uk": (
            "Запрошуй друзів та отримуй бонуси!\n\n"
            "• +5 безкоштовних питань за друга\n"
            "• 10 друзів = 1 місяць преміуму БЕЗКОШТОВНО\n\n"
            "Твоє посилання:"
        ),
    },
    "referral_share": {
        "en": "📤 Share link",
        "ru": "📤 Поделиться ссылкой",
        "uk": "📤 Поділитись посиланням",
    },
    "referral_new_friend": {
        "en": "🎉 New friend joined via your link! +5 questions.",
        "ru": "🎉 Новый друг присоединился по твоей ссылке! +5 вопросов.",
        "uk": "🎉 Новий друг приєднався за твоїм посиланням! +5 питань.",
    },

    # === PREMIUM ===
    "premium_title": {
        "en": "💎 Premium access",
        "ru": "💎 Премиум-доступ",
        "uk": "💎 Преміум-доступ",
    },
    "premium_desc": {
        "en": (
            "What you get:\n"
            "• Unlimited questions\n"
            "• Priority responses\n"
            "• All AI models\n\n"
            "Price: {price} ⭐ (Telegram Stars)\n"
            "Duration: 30 days"
        ),
        "ru": (
            "Что даёт:\n"
            "• Неограниченные вопросы\n"
            "• Приоритетные ответы\n"
            "• Все AI-модели\n\n"
            "Цена: {price} ⭐ (Telegram Stars)\n"
            "Срок: 30 дней"
        ),
        "uk": (
            "Що дає:\n"
            "• Необмежені питання\n"
            "• Пріоритетні відповіді\n"
            "• Всі AI-моделі\n\n"
            "Ціна: {price} ⭐ (Telegram Stars)\n"
            "Термін: 30 днів"
        ),
    },
    "premium_paid": {
        "en": "🎉 Payment received! Premium activated for 30 days.",
        "ru": "🎉 Оплата получена! Премиум активирован на 30 дней.",
        "uk": "🎉 Оплату отримано! Преміум активовано на 30 днів.",
    },

    # === VOICE ===
    "voice_processing": {
        "en": "🎙 Transcribing...",
        "ru": "🎙 Распознаю...",
        "uk": "🎙 Розпізнаю...",
    },
    "voice_error": {
        "en": "⚠️ Could not recognize the voice. Try again.",
        "ru": "⚠️ Не удалось распознать голос. Попробуй ещё раз.",
        "uk": "⚠️ Не вдалося розпізнати голос. Спробуй ще раз.",
    },

    # === ERRORS ===
    "error_generic": {
        "en": "⚠️ Error occurred. Try again later.",
        "ru": "⚠️ Произошла ошибка. Попробуй позже.",
        "uk": "⚠️ Сталася помилка. Спробуй пізніше.",
    },
    "banned": {
        "en": "🚫 You are banned.",
        "ru": "🚫 Ты забанен.",
        "uk": "🚫 Тебе заблоковано.",
    },

    # === ADMIN ===
    "admin_only": {
        "en": "⛔ Admin only.",
        "ru": "⛔ Только для админа.",
        "uk": "⛔ Тільки для адміна.",
    },
    "admin_menu": {
        "en": "👑 Admin panel",
        "ru": "👑 Админ-панель",
        "uk": "👑 Адмін-панель",
    },
}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs) -> str:
    """
    Возвращает перевод строки по ключу для указанного языка.
    Если ключа нет — возвращает сам ключ.
    """
    if key not in TRANSLATIONS:
        return f"[{key}]"

    translations = TRANSLATIONS[key]
    text = translations.get(lang) or translations.get(DEFAULT_LANG) or key

    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass

    return text