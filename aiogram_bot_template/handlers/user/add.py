import shlex
from typing import Final

from aiogram import types

from aiogram_bot_template.db.item import ALLOWED_RARITIES, insert_item, item_exists


ALLOWED_RARITIES_SET: Final[set[str]] = set(ALLOWED_RARITIES)


def parse_add_arguments(text: str) -> tuple[str | None, str | None, str | None, str | None]:
    try:
        parts = shlex.split(text)
    except ValueError:
        return None, None, None, None

    if not parts or not parts[0].startswith("/add"):
        return None, None, None, None

    args = parts[1:]
    if len(args) not in (2, 3, 4):
        return None, None, None, None

    name = args[0].strip()
    description: str | None = None
    price: str | None = None
    rarity: str | None = None

    if len(args) == 2:
        price = args[1].strip()
    elif len(args) == 3:
        if args[1].strip().isdigit():
            price = args[1].strip()
            rarity = args[2].strip().lower()
        else:
            description = args[1].strip() or None
            price = args[2].strip()
    else:
        description = args[1].strip() or None
        price = args[2].strip()
        rarity = args[3].strip().lower()

    return name, description, price, rarity


async def add(msg: types.Message, **kwargs: object) -> None:
    if msg.from_user is None or not msg.text:
        return

    name, description, price_text, rarity = parse_add_arguments(msg.text)
    if name is None or not name:
        await msg.answer("❌ Не указано обязательное поле: название.")
        return

    if price_text is None or not price_text:
        await msg.answer("❌ Не указано обязательное поле: цена.")
        return

    if not price_text.isdigit():
        await msg.answer("❌ Цена должна быть положительным целым числом.")
        return

    price = int(price_text)
    if price <= 0:
        await msg.answer("❌ Цена должна быть положительным целым числом.")
        return

    if rarity is None or rarity == "":
        rarity = "common"
    if rarity not in ALLOWED_RARITIES_SET:
        await msg.answer(
            "❌ Недопустимая редкость.\n"
            "Доступные значения:\n"
            "• common\n"
            "• uncommon\n"
            "• rare\n"
            "• epic\n"
            "• legendary"
        )
        return

    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        await msg.answer("❌ Внутренняя ошибка: отсутствует подключение к базе данных.")
        return

    if await item_exists(db_pool, name):
        await msg.answer("❌ Предмет с таким названием уже существует.")
        return

    await insert_item(db_pool, name, description, price, rarity)

    rarity_capitalized = rarity.capitalize()
    description_text = description if description is not None and description != "" else "-"

    await msg.answer(
        "✅ Предмет успешно добавлен!\n\n"
        f"📦 Название: {name}\n"
        f"📝 Описание: {description_text}\n"
        f"💰 Цена: {price}\n"
        f"⭐ Редкость: {rarity_capitalized}"
    )
