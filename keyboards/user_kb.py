from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.i18n import t


def main_menu_kb(lang: str = "en", is_premium: bool = False) -> InlineKeyboardMarkup:
    """Главное меню юзера."""
    buttons = [
        [InlineKeyboardButton(text=t("btn_ask_ai", lang), callback_data="ask_ai")],
        [
            InlineKeyboardButton(text=t("btn_profile", lang), callback_data="profile"),
            InlineKeyboardButton(text=t("btn_referral", lang), callback_data="referral"),
        ],
    ]

    if not is_premium:
        buttons.append([
            InlineKeyboardButton(text=t("btn_buy_premium", lang), callback_data="buy_premium")
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text=t("btn_premium_active", lang), callback_data="premium_info")
        ])

    buttons.append([
        InlineKeyboardButton(text=t("btn_help", lang), callback_data="help"),
        InlineKeyboardButton(text=t("btn_change_lang", lang), callback_data="change_lang"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def language_kb() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk")],
    ])


def back_to_menu_kb(lang: str = "en") -> InlineKeyboardMarkup:
    """Кнопка 'Назад в меню'."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="main_menu")]
    ])


def buy_premium_kb(lang: str = "en") -> InlineKeyboardMarkup:
    """Клавиатура покупки премиума."""
    from config import PREMIUM_PRICE_STARS
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"💎 Pay {PREMIUM_PRICE_STARS} ⭐",
            callback_data="pay_premium"
        )],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="main_menu")],
    ])


def referral_kb(bot_username: str, user_id: int, lang: str = "en") -> InlineKeyboardMarkup:
    """Клавиатура реферальной системы."""
    link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    share_url = f"https://t.me/share/url?url={link}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("referral_share", lang), url=share_url)],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="main_menu")],
    ])


def profile_kb(lang: str = "en") -> InlineKeyboardMarkup:
    """Клавиатура профиля."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("btn_change_lang", lang), callback_data="change_lang")],
        [InlineKeyboardButton(text=t("btn_back", lang), callback_data="main_menu")],
    ])