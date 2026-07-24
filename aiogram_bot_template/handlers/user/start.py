import asyncpg
from aiogram import html, types
from aiogram.fsm.context import FSMContext

from aiogram_bot_template import states
from aiogram_bot_template.data import config


async def start(msg: types.Message, state: FSMContext) -> None:
    if msg.from_user is None:
        return

    pool = await asyncpg.create_pool(config.PG_LINK, min_size=1, max_size=1)
    try:
        await pool.execute(
            """
            INSERT INTO "user_profile" (telegram_id, first_name, last_name, username)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (telegram_id)
            DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                username = EXCLUDED.username
            """,
            msg.from_user.id,
            msg.from_user.first_name,
            msg.from_user.last_name,
            msg.from_user.username,
        )
    finally:
        await pool.close()

    m = [
        f'Hello, <a href="tg://user?id={msg.from_user.id}">{html.quote(msg.from_user.full_name)}</a>',
    ]
    await msg.answer("\n".join(m))
    await state.set_state(states.user.UserMainMenu.menu)
