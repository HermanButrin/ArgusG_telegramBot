from aiogram import types

from aiogram_bot_template.db.user import promote_user_by_username


async def promote(msg: types.Message, **kwargs: object) -> None:
    if msg.from_user is None:
        return

    if not msg.text:
        await msg.answer("Используйте формат: /promote @username")
        return

    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Используйте формат: /promote @username")
        return

    username = parts[1].strip().lstrip("@")
    if not username:
        await msg.answer("Используйте формат: /promote @username")
        return

    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        return

    updated = await promote_user_by_username(db_pool, username)
    if updated:
        await msg.answer(f"Пользователь @{username} назначен администратором.")
    else:
        await msg.answer(f"Пользователь @{username} не найден.")