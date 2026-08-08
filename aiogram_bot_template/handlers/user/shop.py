from aiogram import html
from aiogram.types import CallbackQuery

from aiogram_bot_template.db.user import get_user, take_user_coins
from aiogram_bot_template.db.item import get_item_by_brand_model
from aiogram_bot_template.db.inventory import add_item_to_inventory
from aiogram_bot_template.keyboards.inline.callbacks import ShopAction
from aiogram_bot_template.keyboards.inline.user.shop import (
    create_shop_brand_keyboard,
    create_shop_model_keyboard,
    create_shop_model_preview_keyboard,
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
        reply_markup=create_shop_type_keyboard(),
    )
    await callback.answer()


async def shop_callback(callback: CallbackQuery, callback_data: ShopAction, **kwargs: object) -> None:  # noqa: C901, PLR0911
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
            reply_markup=create_shop_type_keyboard(),
        )
    elif action == "shop_brands":
        if not instrument_type:
            await callback.answer("Тип инструмента не найден.", show_alert=True)
            return
        await callback.message.edit_text(
            "Выберите бренд:",
            reply_markup=await create_shop_brand_keyboard(db_pool, instrument_type),
        )
    elif action == "shop_models":
        if not instrument_type or not brand:
            await callback.answer("Марка или тип инструмента не найдены.", show_alert=True)
            return
        await callback.message.edit_text(
            "Выберите модель:",
            reply_markup=await create_shop_model_keyboard(db_pool, instrument_type, brand),
        )
    elif action == "shop_model_preview":
        if not instrument_type or not brand or not callback_data.model:
            await callback.answer("Модель не найдена.", show_alert=True)
            return

        item = await get_item_by_brand_model(db_pool, brand, callback_data.model)
        if item is None:
            await callback.answer("Модель не найдена в каталоге.", show_alert=True)
            return

        item_type = str(item.get("type")).title()
        item_brand = str(item.get("brand")).title()
        item_model = str(item.get("model")).title()
        rarity = str(item.get("rarity")).title()
        genre = str(item.get("genre", "")).replace("_", " ").title()
        description = str(item.get("description")) or "Описание отсутствует."
        price = item.get("price")
        is_stackable = bool(item.get("is_stackable"))
        bonus = item.get("proficiency_bonus")

        text = (
            f"<b>{item_brand} {item_model}</b>\n"
            f"Тип: {item_type}\n"
            f"Цена: {price} coins\n"
            f"Редкость: {rarity}\n"
            f"Жанр: {genre}\n"
            f"Стакается: {'Да' if is_stackable else 'Нет'}\n"
            f"Бонус мастерства: +{bonus}\n\n"
            f"{html.quote(description)}"
        )

        await callback.message.edit_text(
            text,
            reply_markup=create_shop_model_preview_keyboard(instrument_type, brand, callback_data.model),
        )
    elif action == "shop_buy":
        if not instrument_type or not brand or not callback_data.model:
            await callback.answer("Модель не найдена.", show_alert=True)
            return

        item = await get_item_by_brand_model(db_pool, brand, callback_data.model)
        user = await get_user(db_pool, callback.from_user.id)
        if user is None:
            await callback.answer("Пользователь не найден.", show_alert=True)
            return

        if item is None:
            await callback.answer("Модель не найдена в каталоге.", show_alert=True)
            return

        if int(user.get("coins")) < int(item.get("price")):
            await callback.answer("У вас недостаточно монет для покупки этого предмета.", show_alert=True)
            return
        await take_user_coins(db_pool, callback.from_user.id, item["price"])
        await add_item_to_inventory(db_pool, callback.from_user.id, item["id"])
        await callback.answer(f"Вы успешно купили {item['brand']} {item['model']} за {item['price']} coins!", show_alert=True)
    else:
        await callback.answer("Выберите раздел магазина.", show_alert=True)
        return

    await callback.answer()
