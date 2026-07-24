import asyncpg
from aiogram import types
from aiogram.filters import Command

from aiogram_bot_template.data import config


async def ban(msg: types.Message, **kwargs: object) -> None:
    if msg.from_user is None:
        return

    if not msg.text:
        await msg.answer("Используйте формат: /ban @username")
        return

    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Используйте формат: /ban @username")
        return

    username = parts[1].strip().lstrip("@")
    if not username:
        await msg.answer("Используйте формат: /ban @username")
        return

    pool = await asyncpg.create_pool(config.PG_LINK, min_size=1, max_size=1)
    try:
        await pool.execute(
            """
            UPDATE "user_profile"
            SET is_banned = TRUE
            WHERE username = $1
            """,
            username,
        )

        affected = await pool.fetchval(
            'SELECT COUNT(*) FROM "user_profile" WHERE username = $1',
            username,
        )

        if affected and int(affected) > 0:
            await msg.answer(f"Пользователь @{username} забанен.")
        else:
            await msg.answer(f"Пользователь @{username} не найден.")
    finally:
        await pool.close()
