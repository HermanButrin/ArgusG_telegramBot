from typing import cast

from aiogram import html, types
from aiogram.types import CallbackQuery
from asyncpg import Pool

from aiogram_bot_template.db.item_db import get_item_by_brand_model
from aiogram_bot_template.db.inventory_db import add_item_to_inventory
from aiogram_bot_template.db.user_db import get_user, take_user_coins
from aiogram_bot_template.keyboards.inline.callbacks import ShopAction
from aiogram_bot_template.keyboards.inline.user.shop_inline import (
    create_shop_brand_keyboard,
    create_shop_model_keyboard,
    create_shop_model_preview_keyboard,
    create_shop_type_keyboard,
)


async def shop(callback: CallbackQuery, **kwargs: object) -> None:
    if not isinstance(callback.message, types.Message):
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


async def shop_callback(
    callback: CallbackQuery,
    callback_data: ShopAction,
    **kwargs: object,
) -> None:
    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        await callback.answer("База данных недоступна.", show_alert=True)
        return

    pool = cast("Pool", db_pool)
    action = callback_data.action
    instrument_type = callback_data.instrument_type or ""
    brand = callback_data.brand or ""

    if action == "shop_types":
        result = await shop_types(callback)
    elif action == "shop_brands":
        result = await shop_brands(callback, instrument_type, pool)
    elif action == "shop_models":
        result = await shop_models(callback, instrument_type, brand, pool)
    elif action == "shop_model_preview":
        result = await shop_model_preview(callback, callback_data, instrument_type, brand, pool)
    elif action == "shop_buy":
        result = await shop_buy(callback, callback_data, instrument_type, brand, pool)
    else:
        result = "Выберите раздел магазина."

    if result is not None:
        await callback.answer(result, show_alert=True)
        return

    await callback.answer()


async def shop_types(callback: CallbackQuery) -> str | None:
    if not isinstance(callback.message, types.Message):
        return None

    await callback.message.edit_text(
        "Выберите тип инструмента:",
        reply_markup=create_shop_type_keyboard(),
    )

    return None


async def shop_brands(
    callback: CallbackQuery,
    instrument_type: str,
    db_pool: Pool,
) -> str | None:
    if not isinstance(callback.message, types.Message):
        return None

    if not instrument_type:
        return "Тип инструмента не найден."

    await callback.message.edit_text(
        "Выберите бренд:",
        reply_markup=await create_shop_brand_keyboard(db_pool, instrument_type),
    )

    return None


async def shop_models(
    callback: CallbackQuery,
    instrument_type: str,
    brand: str,
    db_pool: Pool,
) -> str | None:
    if not isinstance(callback.message, types.Message):
        return None

    if not instrument_type or not brand:
        return "Марка или тип инструмента не найдены."

    await callback.message.edit_text(
        "Выберите модель:",
        reply_markup=await create_shop_model_keyboard(db_pool, instrument_type, brand),
    )

    return None


async def shop_model_preview(
    callback: CallbackQuery,
    callback_data: ShopAction,
    instrument_type: str,
    brand: str,
    db_pool: Pool,
) -> str | None:
    if not isinstance(callback.message, types.Message):
        return None

    model = callback_data.model

    if not instrument_type or not brand or not model:
        return "Модель не найдена."

    item = await get_item_by_brand_model(db_pool, brand, model)

    if item is None:
        return "Модель не найдена в каталоге."

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
        reply_markup=create_shop_model_preview_keyboard(
            instrument_type,
            brand,
            model,
        ),
    )

    return None


async def shop_buy(
    callback: CallbackQuery,
    callback_data: ShopAction,
    instrument_type: str,
    brand: str,
    db_pool: Pool,
) -> str | None:
    model = callback_data.model
    from_user = callback.from_user

    if not instrument_type or not brand or not model:
        return "Модель не найдена."

    item = await get_item_by_brand_model(db_pool, brand, model)

    if item is None:
        return "Модель не найдена в каталоге."

    user = await get_user(db_pool, from_user.id)

    if user is None:
        return "Пользователь не найден."

    price_value = user.get("coins", 0)
    price = price_value if isinstance(price_value, int) else 0
    coins_value = user.get("coins", 0)
    coins = coins_value if isinstance(coins_value, int) else 0

    if coins < price:
        return "У вас недостаточно монет для покупки этого предмета."

    await take_user_coins(db_pool, from_user.id, price)
    await add_item_to_inventory(db_pool, from_user.id, item["id"])

    return f"Вы успешно купили {item['brand']} {item['model']} за {price} coins!"
