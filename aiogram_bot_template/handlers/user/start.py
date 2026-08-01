from aiogram import html, types
from aiogram.fsm.context import FSMContext

from aiogram_bot_template import states
from aiogram_bot_template.db.user import upsert_user


async def start(msg: types.Message, state: FSMContext, **kwargs: object) -> None:
    if msg.from_user is None:
        return

    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        return

    await upsert_user(
        db_pool,
        msg.from_user.id,
        msg.from_user.first_name,
        msg.from_user.last_name,
        msg.from_user.username,
    )

    m = [
        f'Hello, <a href="tg://user?id={msg.from_user.id}">{html.quote(msg.from_user.full_name)}</a>',
    ]
    await msg.answer("\n".join(m))
    await state.set_state(states.user.UserMainMenu.menu)
