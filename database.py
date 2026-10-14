import asyncpg
from datetime import datetime, timedelta
from config import DB_URL

# Глобальный пул соединений
_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=5)
    return _pool


async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                language TEXT DEFAULT 'en',
                questions_used INTEGER DEFAULT 0,
                bonus_questions INTEGER DEFAULT 0,
                is_premium INTEGER DEFAULT 0,
                premium_until TEXT,
                referrer_id BIGINT,
                referrals_count INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                created_at TEXT,
                last_seen TEXT
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                amount INTEGER,
                currency TEXT,
                payload TEXT,
                telegram_payment_id TEXT,
                created_at TEXT
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS messages_log (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                user_message TEXT,
                bot_answer TEXT,
                model TEXT,
                created_at TEXT
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS promocodes (
                code TEXT PRIMARY KEY,
                bonus_questions INTEGER DEFAULT 0,
                bonus_premium_days INTEGER DEFAULT 0,
                max_uses INTEGER DEFAULT 0,
                used_count INTEGER DEFAULT 0,
                created_at TEXT
            )
        """)


# ============ USER ============

async def get_user(user_id: int):
    """Возвращает кортеж для совместимости со старым кодом (индексы 0-12)."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        if not row:
            return None
        return (
            row["user_id"],          # 0
            row["username"],         # 1
            row["first_name"],       # 2
            row["language"],         # 3
            row["questions_used"],   # 4
            row["bonus_questions"],  # 5
            row["is_premium"],       # 6
            row["premium_until"],    # 7
            row["referrer_id"],      # 8
            row["referrals_count"],  # 9
            row["is_banned"],        # 10
            row["created_at"],       # 11
            row["last_seen"],        # 12
        )


async def add_user(user_id: int, username: str, first_name: str, referrer_id: int = None):
    now = datetime.utcnow().isoformat()
    pool = await get_pool()
    async with pool.acquire() as conn:
        exists = await conn.fetchrow("SELECT user_id FROM users WHERE user_id = $1", user_id)
        if not exists:
            await conn.execute("""
                INSERT INTO users (user_id, username, first_name, referrer_id, created_at, last_seen)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, user_id, username, first_name, referrer_id, now, now)
            if referrer_id:
                await conn.execute("""
                    UPDATE users SET bonus_questions = bonus_questions + 5,
                        referrals_count = referrals_count + 1
                    WHERE user_id = $1
                """, referrer_id)
        else:
            await conn.execute("""
                UPDATE users SET last_seen = $1, username = $2, first_name = $3
                WHERE user_id = $4
            """, now, username, first_name, user_id)


async def inc_questions(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT questions_used, bonus_questions FROM users WHERE user_id = $1", user_id
        )
        if not row:
            return
        bonus = row["bonus_questions"]
        if bonus > 0:
            await conn.execute(
                "UPDATE users SET bonus_questions = bonus_questions - 1 WHERE user_id = $1", user_id
            )
        else:
            await conn.execute(
                "UPDATE users SET questions_used = questions_used + 1 WHERE user_id = $1", user_id
            )


async def get_questions_left(user_id: int):
    from config import FREE_LIMIT
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT questions_used, bonus_questions, is_premium FROM users WHERE user_id = $1", user_id
        )
    if not row:
        return 0
    used = row["questions_used"]
    bonus = row["bonus_questions"]
    is_premium = row["is_premium"]
    if is_premium:
        return 999999
    return max(0, FREE_LIMIT + bonus - used)


async def set_premium(user_id: int, days: int = 30):
    until = (datetime.utcnow() + timedelta(days=days)).isoformat()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET is_premium = 1, premium_until = $1 WHERE user_id = $2", until, user_id
        )


async def remove_premium(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET is_premium = 0, premium_until = NULL WHERE user_id = $1", user_id
        )


async def ban_user(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET is_banned = 1 WHERE user_id = $1", user_id)


async def unban_user(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET is_banned = 0 WHERE user_id = $1", user_id)


# ============ PAYMENTS ============

async def add_payment(user_id: int, amount: int, currency: str, payload: str, tg_payment_id: str):
    now = datetime.utcnow().isoformat()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO payments (user_id, amount, currency, payload, telegram_payment_id, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, user_id, amount, currency, payload, tg_payment_id, now)


# ============ LOGS ============

async def log_message(user_id: int, user_message: str, bot_answer: str, model: str):
    now = datetime.utcnow().isoformat()
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO messages_log (user_id, user_message, bot_answer, model, created_at)
            VALUES ($1, $2, $3, $4, $5)
        """, user_id, user_message, bot_answer, model, now)


# ============ STATS ============

async def get_stats():
    pool = await get_pool()
    async with pool.acquire() as conn:
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
        premium_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_premium = 1")
        banned_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE is_banned = 1")
        total_payments = await conn.fetchval("SELECT COUNT(*) FROM payments")
        total_stars = await conn.fetchval("SELECT COALESCE(SUM(amount), 0) FROM payments")
        total_messages = await conn.fetchval("SELECT COUNT(*) FROM messages_log")
    return {
        "total_users": total_users,
        "premium_users": premium_users,
        "banned_users": banned_users,
        "total_payments": total_payments,
        "total_stars": total_stars,
        "total_messages": total_messages,
    }


async def get_all_user_ids():
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM users WHERE is_banned = 0")
    return [r["user_id"] for r in rows]


async def get_referral_top(limit: int = 10):
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT user_id, username, first_name, referrals_count
            FROM users
            WHERE referrals_count > 0
            ORDER BY referrals_count DESC
            LIMIT $1
        """, limit)
    return [
        (r["user_id"], r["username"], r["first_name"], r["referrals_count"])
        for r in rows
    ]


# ============ LANGUAGE ============

async def set_language(user_id: int, lang: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET language = $1 WHERE user_id = $2", lang, user_id)


async def get_language(user_id: int) -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT language FROM users WHERE user_id = $1", user_id)
    return row["language"] if row and row["language"] else "en"