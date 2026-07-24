import random
from datetime import datetime, timezone

import asyncpg
from aiogram import types

from aiogram_bot_template.data import config


async def coin(msg: types.Message) -> None:
    if msg.from_user is None:
        return

    amount = random.randint(5, 10)

    pool = await asyncpg.create_pool(config.PG_LINK, min_size=1, max_size=1)
    try:
        user_row = await pool.fetchrow(
            """
            SELECT coins_cooldown
            FROM "user"
            WHERE telegram_id = $1
            """,
            msg.from_user.id,
        )

        now = datetime.now(timezone.utc)
        cooldown_until = user_row["coins_cooldown"] if user_row is not None else None

        if cooldown_until is not None and cooldown_until > now:
            remaining_seconds = int((cooldown_until - now).total_seconds())
            hours, remainder = divmod(remaining_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            await msg.answer(
                f"Вы сможете получить монеты снова через {hours} ч {minutes} мин {seconds} сек.⏳",
            )
            return

        cooldown_until = now.fromtimestamp(int(now.timestamp()) + 3600, tz=timezone.utc)

        await pool.execute(
            """
            INSERT INTO "user" (telegram_id, coins, coins_cooldown)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id)
            DO UPDATE SET
                coins = "user".coins + EXCLUDED.coins,
                coins_cooldown = EXCLUDED.coins_cooldown
            """,
            msg.from_user.id,
            amount,
            cooldown_until,
        )

        await msg.answer(f"Вы получили {amount} монет! 🎉")
    finally:
        await pool.close()
