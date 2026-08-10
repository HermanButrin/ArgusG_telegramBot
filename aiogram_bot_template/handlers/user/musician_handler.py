from aiogram import types
from aiogram.types import CallbackQuery

from aiogram_bot_template.db.inventory_db import find_useritem_by_user_id
from aiogram_bot_template.keyboards.inline.user.back_inline import create_back
from aiogram_bot_template.keyboards.inline.user.musician_inline import (
    create_musician_menu,
)


async def musician(callback: CallbackQuery, **kwargs: object) -> None:
    if not isinstance(callback.message, types.Message):
        await callback.answer()
        return

    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        await callback.answer("База данных недоступна.", show_alert=True)
        return

    await callback.message.edit_text(
        "Выберите тип инструмента:",
        reply_markup=create_musician_menu(),
    )

    await callback.answer()


async def inventory(callback: CallbackQuery, **kwargs: object) -> None:
    if not isinstance(callback.message, types.Message):
        await callback.answer()
        return

    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        await callback.answer("База данных недоступна.", show_alert=True)
        return

    from_user = callback.from_user

    inventory_items = await find_useritem_by_user_id(db_pool, from_user.id)

    if not inventory_items:
        text = "Ваш инвентарь пуст."
    else:
        items = "\n".join(
            f"• {item['brand']} {item['model']} × {item['quantity']}"
            for item in inventory_items
        )
        text = f"Ваш инвентарь:\n\n{items}"

    await callback.message.edit_text(
        text,
        reply_markup=create_back("musician"),
    )

    await callback.answer()
