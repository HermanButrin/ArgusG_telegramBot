import shlex
from typing import Final

from aiogram import types

from aiogram_bot_template.db.item import (
    ALLOWED_GENRES,
    ALLOWED_RARITIES,
    insert_item,
    item_exists,
    remove_item,
)


ALLOWED_RARITIES_SET: Final[set[str]] = set(ALLOWED_RARITIES)
ALLOWED_GENRES_SET: Final[set[str]] = set(ALLOWED_GENRES)

ITEM_ADD_ARGUMENTS_COUNT: Final = 7
ITEM_REMOVE_ARGUMENTS_COUNT: Final = 1


def parse_item_command(text: str) -> list[str] | None:
    try:
        parts = shlex.split(text)
    except ValueError:
        return None

    if not parts or parts[0] != "/item":
        return None

    return parts[1:]


async def item(msg: types.Message, **kwargs: object) -> None:
    if msg.from_user is None or not msg.text:
        return

    args = parse_item_command(msg.text)

    if args is None:
        return

    if not args:
        await msg.answer(
            "📦 Использование команды:\n\n"
            "/item add — добавить предмет\n"
            "/item remove — удалить предмет\n\n"
            "Пример:\n"
            '/item add "Flying V" "Черная гитара" 500 epic '
            '"Heavy Metal" false 5',
        )
        return

    action = args[0].lower()

    if action == "add":
        await item_add(msg, args[1:], kwargs)
        return

    if action == "remove":
        await item_remove(msg, args[1:], kwargs)
        return

    await msg.answer(
        "❌ Неизвестная команда.\n"
        "Используй:\n"
        "/item\n"
        "/item add\n"
        "/item remove",
    )

# --- Добавление предмета ---

# ruff: noqa: PLR0911
async def item_add(
    msg: types.Message,
    args: list[str],
    kwargs: dict,
) -> None:

    if len(args) != ITEM_ADD_ARGUMENTS_COUNT:
        await msg.answer(
            "❌ Формат:\n"
            "/item add название описание цена редкость жанр stackable bonus",
        )
        return

    name, description, price_text, rarity, genre, stackable_text, bonus_text = (
        args[0],
        args[1],
        args[2],
        args[3].lower(),
        args[4].lower(),
        args[5].lower(),
        args[6],
    )

    if not price_text.isdigit():
        await msg.answer("❌ Цена должна быть числом.")
        return

    price = int(price_text)

    if rarity not in ALLOWED_RARITIES_SET:
        await msg.answer(
            "❌ Неверная редкость.",
        )
        return

    if genre not in ALLOWED_GENRES_SET:
        await msg.answer(
            "❌ Неверный жанр.\n"
            + "\n".join(ALLOWED_GENRES),
        )
        return

    if stackable_text not in {"true", "false"}:
        await msg.answer(
            "❌ stackable должен быть true или false",
        )
        return

    if not bonus_text.isdigit():
        await msg.answer(
            "❌ proficiency_bonus должен быть числом",
        )
        return

    proficiency_bonus = int(bonus_text)
    is_stackable = stackable_text == "true"

    pool = kwargs.get("db_pool")

    if pool is None:
        await msg.answer("❌ Ошибка базы данных.")
        return

    if await item_exists(pool, name):
        await msg.answer(
            "❌ Такой предмет уже существует.",
        )
        return

    await insert_item(
        pool,
        name,
        description,
        price,
        rarity,
        is_stackable,
        genre,
        proficiency_bonus,
    )

    await msg.answer(
        "✅ Предмет создан!\n\n"
        f"📦 {name}\n"
        f"💰 Цена: {price}\n"
        f"⭐ {rarity}\n"
        f"🎸 Жанр: {genre}\n"
        f"⚔ Бонус: +{proficiency_bonus}\n"
        f"📚 Stackable: {is_stackable}",
    )

# --- Удаление предмета ---


async def item_remove(
    msg: types.Message,
    args: list[str],
    kwargs: dict,
) -> None:

    if len(args) != ITEM_REMOVE_ARGUMENTS_COUNT:
        await msg.answer(
            "❌ Использование:\n"
            "/item remove название",
        )
        return

    pool = kwargs.get("db_pool")

    if pool is None:
        await msg.answer("❌ Ошибка базы данных.")
        return

    deleted = await remove_item(
        pool,
        args[0],
    )

    if not deleted:
        await msg.answer(
            "❌ Предмет не найден.",
        )
        return

    await msg.answer(
        f"🗑 Предмет {args[0]} удалён.",
    )
