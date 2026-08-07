from asyncpg import Pool
from aiogram.types import InlineKeyboardMarkup

from aiogram_bot_template.db.item import (
    fetch_distinct_brands_by_type,
    fetch_distinct_models_by_brand,
    fetch_distinct_types,
)
from aiogram_bot_template.keyboards.inline.callbacks import Action, ShopAction
from aiogram_bot_template.keyboards.inline.consts import InlineConstructor


def _keyboard_rows(actions: list[dict[str, object]], rows_per_line: int = 1) -> list[int]:
    if not actions:
        return []

    chunks: list[int] = []
    remaining = len(actions)
    while remaining > 0:
        current = min(rows_per_line, remaining)
        chunks.append(current)
        remaining -= current

    return chunks


async def create_shop_type_keyboard(pool: Pool) -> InlineKeyboardMarkup:
    instrument_types = await fetch_distinct_types(pool)

    actions = [
        {
            "text": instrument_type.replace("_", " ").title(),
            "callback_data": ShopAction(
                action="shop_brands",
                instrument_type=instrument_type,
            ),
        }
        for instrument_type in instrument_types
    ]
    actions.append({"text": "◀️ Назад", "callback_data": Action(action="menu")})

    return InlineConstructor.create_keyboard(actions, _keyboard_rows(actions))


async def create_shop_brand_keyboard(pool: Pool, instrument_type: str) -> InlineKeyboardMarkup:
    brands = await fetch_distinct_brands_by_type(pool, instrument_type)

    actions = [
        {
            "text": brand.title(),
            "callback_data": ShopAction(
                action="shop_models",
                instrument_type=instrument_type,
                brand=brand,
            ),
        }
        for brand in brands
    ]
    actions.append(
        {
            "text": "◀️ Назад",
            "callback_data": ShopAction(action="shop_types"),
        },
    )

    return InlineConstructor.create_keyboard(actions, _keyboard_rows(actions))


async def create_shop_model_keyboard(pool: Pool, instrument_type: str, brand: str) -> InlineKeyboardMarkup:
    models = await fetch_distinct_models_by_brand(pool, instrument_type, brand)

    actions = [
        {
            "text": model.title(),
            "callback_data": ShopAction(
                action="shop_model_preview",
                instrument_type=instrument_type,
                brand=brand,
                model=model,
            ),
        }
        for model in models
    ]
    actions.append(
        {
            "text": "◀️ Назад",
            "callback_data": ShopAction(
                action="shop_brands",
                instrument_type=instrument_type,
            ),
        },
    )

    return InlineConstructor.create_keyboard(actions, _keyboard_rows(actions))
