from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.i18n import t


def admin_menu_kb(lang: str = "en") -> InlineKeyboardMarkup:
    """Главное меню админа."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Stats", callback_data="admin_stats"),
            InlineKeyboardButton(text="👥 Users", callback_data="admin_users"),
        ],
        [
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton(text="💰 Payments", callback_data="admin_payments"),
        ],
        [
            InlineKeyboardButton(text="🏆 Top Referrers", callback_data="admin_referrals"),
            InlineKeyboardButton(text="🎁 Promocodes", callback_data="admin_promo"),
        ],
        [InlineKeyboardButton(text="⬅️ Close", callback_data="admin_close")],
    ])


def admin_back_kb() -> InlineKeyboardMarkup:
    """Кнопка 'Назад' в админке."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back to admin", callback_data="admin_menu")]
    ])


def admin_confirm_broadcast_kb() -> InlineKeyboardMarkup:
    """Подтверждение рассылки."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Send", callback_data="admin_broadcast_confirm"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="admin_menu"),
        ]
    ])


def admin_user_actions_kb(user_id: int, is_premium: int, is_banned: int) -> InlineKeyboardMarkup:
    """Действия над конкретным юзером."""
    buttons = []

    if is_premium:
        buttons.append([InlineKeyboardButton(
            text="❌ Remove Premium",
            callback_data=f"admin_remove_premium_{user_id}"
        )])
    else:
        buttons.append([InlineKeyboardButton(
            text="👑 Give Premium",
            callback_data=f"admin_give_premium_{user_id}"
        )])

    if is_banned:
        buttons.append([InlineKeyboardButton(
            text="✅ Unban",
            callback_data=f"admin_unban_{user_id}"
        )])
    else:
        buttons.append([InlineKeyboardButton(
            text="🚫 Ban",
            callback_data=f"admin_ban_{user_id}"
        )])

    buttons.append([InlineKeyboardButton(text="⬅️ Back", callback_data="admin_users")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)