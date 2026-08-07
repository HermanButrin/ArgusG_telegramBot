from aiogram.types import CallbackQuery

from aiogram_bot_template.keyboards.inline.callbacks import ShopAction
from aiogram_bot_template.keyboards.inline.user.shop import (
    create_shop_brand_keyboard,
    create_shop_model_keyboard,
    create_shop_type_keyboard,
)


async def shop(callback: CallbackQuery, **kwargs: object) -> None:
    if callback.message is None:
        await callback.answer()
        return

    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        await callback.answer("База данных недоступна.", show_alert=True)
        return

    await callback.message.edit_text(
        "Выберите тип инструмента:",
        reply_markup=await create_shop_type_keyboard(db_pool),
    )
    await callback.answer()


async def shop_callback(callback: CallbackQuery, callback_data: ShopAction, **kwargs: object) -> None:
    if callback.message is None:
        await callback.answer()
        return

    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        await callback.answer("База данных недоступна.", show_alert=True)
        return

    action = callback_data.action
    instrument_type = callback_data.instrument_type or ""
    brand = callback_data.brand or ""

    if action == "shop_types":
        await callback.message.edit_text(
            "Выберите тип инструмента:",
            reply_markup=await create_shop_type_keyboard(db_pool),
        )
    elif action == "shop_brands":
        if not instrument_type:
            await callback.answer("Тип инструмента не найден.", show_alert=True)
            return
        await callback.message.edit_text(
            f"Выберите бренд для {instrument_type.replace('_', ' ').title()}:",
            reply_markup=await create_shop_brand_keyboard(db_pool, instrument_type),
        )
    elif action == "shop_models":
        if not instrument_type or not brand:
            await callback.answer("Марка или тип инструмента не найдены.", show_alert=True)
            return
        await callback.message.edit_text(
            f"Выберите модель для {brand} {instrument_type.replace('_', ' ').title()}:",
            reply_markup=await create_shop_model_keyboard(db_pool, instrument_type, brand),
        )
    else:
        await callback.answer("Выберите раздел магазина.", show_alert=True)
        return

    await callback.answer()
