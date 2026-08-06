from typing import Final
from aiogram import types

from aiogram_bot_template.db.user import unban_user_by_username

ARGUMENTS_COUNT: Final = 2


async def unban(msg: types.Message, **kwargs: object) -> None:
    if msg.from_user is None:
        return

    if not msg.text:
        await msg.answer("Используйте формат: /unban @username")
        return

    parts = msg.text.split(maxsplit=1)
    if len(parts) != ARGUMENTS_COUNT:
        await msg.answer("Используйте формат: /unban @username")
        return

    username = parts[1].strip().lstrip("@")
    if not username:
        await msg.answer("Используйте формат: /unban @username")
        return

    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        return

    updated = await unban_user_by_username(db_pool, username)
    if updated:
        await msg.answer(f"Пользователь @{username} разбанен.")
    else:
        await msg.answer(f"Пользователь @{username} не найден.")
