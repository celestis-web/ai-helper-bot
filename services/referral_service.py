from config import REFERRAL_BONUS, REFERRAL_PREMIUM_THRESHOLD


def build_referral_link(bot_username: str, user_id: int) -> str:
    """Создаёт реферальную ссылку."""
    return f"https://t.me/{bot_username}?start=ref_{user_id}"


def parse_referral_param(start_param: str):
    """
    Извлекает ID реферера из параметра 'ref_12345'.
    Возвращает None, если параметр невалидный.
    """
    if not start_param or not start_param.startswith("ref_"):
        return None
    try:
        return int(start_param[4:])
    except ValueError:
        return None


def is_premium_earned(referrals_count: int) -> bool:
    """Проверяет, заработал ли юзер премиум за рефералов."""
    return referrals_count >= REFERRAL_PREMIUM_THRESHOLD