from aiogram import html, types

from aiogram_bot_template.db.user_db import upsert_user
from aiogram_bot_template.keyboards.inline.user.start_menu_inline import create_start_menu
from aiogram.types import CallbackQuery


async def menu(msg: types.Message, **kwargs: object) -> None:
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

    await msg.answer(
        f"Привет, <a href='tg://user?id={msg.from_user.id}'>{html.quote(msg.from_user.full_name)}</a>!\n"
        "Выберите действие в меню ниже:",
        reply_markup=create_start_menu(),
    )


async def menu_callback(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer()
        return

    await callback.message.edit_text(
            f"Привет, <a href='tg://user?id={callback.from_user.id}'>{html.quote(callback.from_user.full_name)}</a>!\n"
            "Выберите действие в меню ниже:",
            reply_markup=create_start_menu(),
        )
    await callback.answer()
