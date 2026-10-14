from aiogram import Router, F
from aiogram.types import Message

from database import get_user
from services.i18n import t
from services.referral_service import is_premium_earned
from database import set_premium

router = Router()


async def notify_referrer(bot, referrer_id: int, new_user_name: str):
    """
    Уведомляет реферера о новом друге и проверяет бонус-премиум.
    """
    try:
        referrer = await get_user(referrer_id)
        if not referrer:
            return

        lang = referrer[3] or "en"
        referrals_count = referrer[9]

        # Уведомление о новом друге
        try:
            await bot.send_message(
                referrer_id,
                t("referral_new_friend", lang),
            )
        except Exception:
            pass

        # Проверка: заработал ли премиум за 10 друзей
        if is_premium_earned(referrals_count) and not referrer[6]:
            await set_premium(referrer_id, days=30)
            bonus_text = {
                "en": "🎉 You invited 10 friends! Premium activated for 30 days FREE!",
                "ru": "🎉 Ты пригласил 10 друзей! Премиум активирован на 30 дней БЕСПЛАТНО!",
                "uk": "🎉 Ти запросив 10 друзів! Преміум активовано на 30 днів БЕЗКОШТОВНО!",
            }
            try:
                await bot.send_message(referrer_id, bonus_text.get(lang, bonus_text["en"]))
            except Exception:
                pass
    except Exception:
        pass