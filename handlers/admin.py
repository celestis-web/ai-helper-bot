from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from database import (
    get_stats, get_all_user_ids, get_user, set_premium,
    remove_premium, ban_user, unban_user, get_referral_top,
)
from keyboards.admin_kb import (
    admin_menu_kb, admin_back_kb, admin_confirm_broadcast_kb,
    admin_user_actions_kb,
)

router = Router()

# Проверка на админа для всего роутера
router.message.filter(F.from_user.id == ADMIN_ID)
router.callback_query.filter(F.from_user.id == ADMIN_ID)


class BroadcastState(StatesGroup):
    waiting_for_text = State()


# ============ /admin ============
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    await message.answer("👑 Admin panel", reply_markup=admin_menu_kb())


# ============ Stats ============
@router.callback_query(F.data == "admin_stats")
async def cb_stats(callback: CallbackQuery):
    s = await get_stats()
    text = (
        "📊 *Statistics*\n\n"
        f"👥 Total users: *{s['total_users']}*\n"
        f"👑 Premium users: *{s['premium_users']}*\n"
        f"🚫 Banned users: *{s['banned_users']}*\n\n"
        f"💰 Payments: *{s['total_payments']}*\n"
        f"⭐ Total Stars: *{s['total_stars']}*\n"
        f"💬 Messages logged: *{s['total_messages']}*"
    )
    await callback.message.edit_text(text, reply_markup=admin_back_kb(), parse_mode="Markdown")
    await callback.answer()


# ============ Users list ============
@router.callback_query(F.data == "admin_users")
async def cb_users(callback: CallbackQuery):
    text = (
        "👥 *User management*\n\n"
        "Send me a user ID to view/ban/premium:\n\n"
        "Example: `8794296833`"
    )
    await callback.message.edit_text(text, reply_markup=admin_back_kb(), parse_mode="Markdown")
    await callback.answer()


@router.message(F.text.regexp(r"^\d+$"))
async def handle_user_id(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    user_id = int(message.text)
    user = await get_user(user_id)

    if not user:
        await message.answer(f"❌ User `{user_id}` not found.", parse_mode="Markdown")
        return

    is_premium = bool(user[6])
    is_banned = bool(user[10])

    text = (
        f"👤 *User info*\n\n"
        f"🆔 ID: `{user[0]}`\n"
        f"📛 Name: {user[2]}\n"
        f"🔗 Username: @{user[1] or '—'}\n"
        f"🌍 Language: {user[3]}\n"
        f"❓ Questions used: {user[4]}\n"
        f"🎁 Bonus questions: {user[5]}\n"
        f"👑 Premium: {'Yes' if is_premium else 'No'}\n"
        f"🚫 Banned: {'Yes' if is_banned else 'No'}\n"
        f"👥 Referrals: {user[9]}"
    )

    await message.answer(
        text,
        reply_markup=admin_user_actions_kb(user_id, int(is_premium), int(is_banned)),
        parse_mode="Markdown",
    )


# ============ User actions ============
@router.callback_query(F.data.startswith("admin_give_premium_"))
async def cb_give_premium(callback: CallbackQuery):
    user_id = int(callback.data.replace("admin_give_premium_", ""))
    await set_premium(user_id, days=30)
    await callback.answer("✅ Premium given!", show_alert=True)
    # обновляем клавиатуру
    user = await get_user(user_id)
    await callback.message.edit_reply_markup(
        reply_markup=admin_user_actions_kb(user_id, 1, int(bool(user[10])))
    )


@router.callback_query(F.data.startswith("admin_remove_premium_"))
async def cb_remove_premium(callback: CallbackQuery):
    user_id = int(callback.data.replace("admin_remove_premium_", ""))
    await remove_premium(user_id)
    await callback.answer("❌ Premium removed", show_alert=True)
    user = await get_user(user_id)
    await callback.message.edit_reply_markup(
        reply_markup=admin_user_actions_kb(user_id, 0, int(bool(user[10])))
    )


@router.callback_query(F.data.startswith("admin_ban_"))
async def cb_ban(callback: CallbackQuery):
    user_id = int(callback.data.replace("admin_ban_", ""))
    await ban_user(user_id)
    await callback.answer("🚫 User banned", show_alert=True)
    user = await get_user(user_id)
    await callback.message.edit_reply_markup(
        reply_markup=admin_user_actions_kb(user_id, int(bool(user[6])), 1)
    )


@router.callback_query(F.data.startswith("admin_unban_"))
async def cb_unban(callback: CallbackQuery):
    user_id = int(callback.data.replace("admin_unban_", ""))
    await unban_user(user_id)
    await callback.answer("✅ User unbanned", show_alert=True)
    user = await get_user(user_id)
    await callback.message.edit_reply_markup(
        reply_markup=admin_user_actions_kb(user_id, int(bool(user[6])), 0)
    )


# ============ Broadcast ============
@router.callback_query(F.data == "admin_broadcast")
async def cb_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📢 *Broadcast*\n\nSend the message you want to broadcast to all users.",
        reply_markup=admin_back_kb(),
        parse_mode="Markdown",
    )
    await state.set_state(BroadcastState.waiting_for_text)
    await callback.answer()


@router.message(BroadcastState.waiting_for_text)
async def process_broadcast_text(message: Message, state: FSMContext):
    await state.update_data(broadcast_text=message.text)
    await message.answer(
        f"📢 Preview:\n\n{message.text}\n\nSend to all users?",
        reply_markup=admin_confirm_broadcast_kb(),
    )


@router.callback_query(F.data == "admin_broadcast_confirm")
async def cb_broadcast_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("broadcast_text")

    if not text:
        await callback.answer("❌ No text", show_alert=True)
        return

    user_ids = await get_all_user_ids()
    sent = 0
    failed = 0

    await callback.message.edit_text(f"📢 Sending to {len(user_ids)} users...")

    for uid in user_ids:
        try:
            await callback.bot.send_message(uid, text)
            sent += 1
        except Exception:
            failed += 1

    await callback.message.edit_text(
        f"✅ Broadcast done!\n\n✔️ Sent: {sent}\n❌ Failed: {failed}",
        reply_markup=admin_back_kb(),
    )
    await state.clear()
    await callback.answer()


# ============ Payments ============
@router.callback_query(F.data == "admin_payments")
async def cb_payments(callback: CallbackQuery):
    text = "💰 *Payments*\n\nComing soon — will show payment history."
    await callback.message.edit_text(text, reply_markup=admin_back_kb(), parse_mode="Markdown")
    await callback.answer()


# ============ Referral top ============
@router.callback_query(F.data == "admin_referrals")
async def cb_referrals(callback: CallbackQuery):
    top = await get_referral_top(10)

    if not top:
        text = "🏆 *Top Referrers*\n\n_No referrers yet._"
    else:
        lines = ["🏆 *Top Referrers*\n"]
        for i, (uid, username, first_name, count) in enumerate(top, 1):
            name = first_name or username or f"User {uid}"
            lines.append(f"{i}. {name} — *{count}* invites")
        text = "\n".join(lines)

    await callback.message.edit_text(text, reply_markup=admin_back_kb(), parse_mode="Markdown")
    await callback.answer()


# ============ Promo ============
@router.callback_query(F.data == "admin_promo")
async def cb_promo(callback: CallbackQuery):
    text = "🎁 *Promocodes*\n\nComing soon — will allow creating promo codes."
    await callback.message.edit_text(text, reply_markup=admin_back_kb(), parse_mode="Markdown")
    await callback.answer()


# ============ Back to admin menu ============
@router.callback_query(F.data == "admin_menu")
async def cb_admin_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("👑 Admin panel", reply_markup=admin_menu_kb())
    await callback.answer()


# ============ Close ============
@router.callback_query(F.data == "admin_close")
async def cb_admin_close(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()