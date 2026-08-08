from asyncpg import Pool
from aiogram.types import InlineKeyboardMarkup

from aiogram_bot_template.db.item_db import (
    ALLOWED_TYPES,
    ALLOWED_RARITIES,
    get_distinct_brands_by_type,
    get_models_with_rarity_by_brand,
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


def create_shop_type_keyboard() -> InlineKeyboardMarkup:
    actions = [
        {
            "text": instrument_type.replace("_", " ").title(),
            "callback_data": ShopAction(
                action="shop_brands",
                instrument_type=instrument_type,
            ),
        }
        for instrument_type in ALLOWED_TYPES
    ]
    actions.append({"text": "◀️ Назад", "callback_data": Action(action="menu")})

    return InlineConstructor.create_keyboard(actions, _keyboard_rows(actions))


async def create_shop_brand_keyboard(pool: Pool, instrument_type: str) -> InlineKeyboardMarkup:
    brands = await get_distinct_brands_by_type(pool, instrument_type)

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
    models = await get_models_with_rarity_by_brand(pool, instrument_type, brand)

    actions = [
        {
            "text": f"{ALLOWED_RARITIES.get(model['rarity'], '')} {model['model'].title()}",
            "callback_data": ShopAction(
                action="shop_model_preview",
                instrument_type=instrument_type,
                brand=brand,
                model=model["model"],
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


def create_shop_model_preview_keyboard(
    instrument_type: str,
    brand: str,
    model: str,
) -> InlineKeyboardMarkup:
    return InlineConstructor.create_keyboard(
        [
            {
                "text": "💰 Купить",
                "callback_data": ShopAction(
                    action="shop_buy",
                    instrument_type=instrument_type,
                    brand=brand,
                    model=model,
                ),
            },
            {
                "text": "◀️ Назад",
                "callback_data": ShopAction(
                    action="shop_models",
                    instrument_type=instrument_type,
                    brand=brand,
                ),
            },
        ],
        [1, 1],
    )
