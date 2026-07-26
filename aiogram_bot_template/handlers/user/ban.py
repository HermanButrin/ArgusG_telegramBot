from aiogram import types
from aiogram.filters import Command

from aiogram_bot_template.db.user import ban_user_by_username


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

    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        return

    updated = await ban_user_by_username(db_pool, username)
    if updated:
        await msg.answer(f"Пользователь @{username} забанен.")
    else:
        await msg.answer(f"Пользователь @{username} не найден.")
