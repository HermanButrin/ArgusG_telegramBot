import shlex
from typing import Final

from aiogram import types

from aiogram_bot_template.db.item import (
    ALLOWED_GENRES,
    ALLOWED_RARITIES,
    ALLOWED_TYPES,
    insert_item,
    item_exists,
    remove_item,
)

ALLOWED_RARITIES_SET: Final[set[str]] = set(ALLOWED_RARITIES)
ALLOWED_GENRES_SET: Final[set[str]] = set(ALLOWED_GENRES)
ALLOWED_TYPES_SET: Final[set[str]] = set(ALLOWED_TYPES)

ITEM_ADD_ARGUMENTS_COUNT: Final = 9
ITEM_REMOVE_ARGUMENTS_COUNT: Final = 3


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
            "📦 <b>Управление предметами</b>\n\n"
            "<b>Доступные команды:</b>\n"
            "• <code>/item add</code> — добавить предмет\n"
            "• <code>/item remove</code> — удалить предмет\n\n"
            "<b>Формат:</b>\n"
            '<code>/item add "Тип" "Бренд" "Модель" '
            '"Описание" Цена Редкость Жанр Stackable Бонус</code>\n\n'
            "<b>Пример:</b>\n"
            '<code>/item add "guitar" "Gibson" "Flying V" '
            '"Черная электрогитара" 1000 epic "heavy metal" true 5</code>\n\n'
            "<b>Допустимые значения:</b>\n"
            f"🎸 <b>Тип:</b> {', '.join(ALLOWED_TYPES)}\n"
            f"⭐ <b>Редкость:</b> {', '.join(ALLOWED_RARITIES)}\n"
            f"🎵 <b>Жанр:</b>\n• " + "\n• ".join(ALLOWED_GENRES) + "\n\n"
            "📚 <b>Stackable:</b> true / false\n"
            "⚔ <b>Бонус:</b> целое число",
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
            "❌ <b>Формат:</b>\n"
            '<code>/item add "Тип" "Бренд" "Модель" '
            '"Описание" Цена Редкость Жанр Stackable Бонус</code>',
        )
        return

    instrument_type, brand, model, description, price_text, rarity, genre, stackable_text, bonus_text = (
        args[0].lower(),
        args[1].lower(),
        args[2].lower(),
        args[3],
        args[4],
        args[5].lower(),
        args[6].lower(),
        args[7].lower(),
        args[8],
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
            "❌ Неверный жанр.\n" + "\n".join(ALLOWED_GENRES),
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

    if await item_exists(pool, instrument_type, brand, model):
        await msg.answer(
            "❌ Такой предмет уже существует.",
        )
        return

    await insert_item(
        pool,
        instrument_type,
        brand,
        model,
        description,
        price,
        rarity,
        is_stackable,
        genre,
        proficiency_bonus,
    )

    await msg.answer(
        "✅ Предмет создан!\n"
        f"🎸 {brand} {model} ({instrument_type})\n"
        f"⭐ {rarity} • 🎵 {genre}\n"
        f"💰 {price}$ • ⚔ +{proficiency_bonus}",
    )


# --- Удаление предмета ---


async def item_remove(
    msg: types.Message,
    args: list[str],
    kwargs: dict,
) -> None:

    if len(args) != ITEM_REMOVE_ARGUMENTS_COUNT:
        await msg.answer(
            "❌ Использование:\n/item remove тип бренд модель",
        )
        return

    instrument_type, brand, model = (
        args[0].lower(),
        args[1].lower(),
        args[2].lower(),
    )

    pool = kwargs.get("db_pool")

    if pool is None:
        await msg.answer("❌ Ошибка базы данных.")
        return

    deleted = await remove_item(
        pool,
        instrument_type,
        brand,
        model,
    )

    if not deleted:
        await msg.answer(
            "❌ Предмет не найден.",
        )
        return

    await msg.answer(
        f"🗑 Предмет {brand} {model} удалён.",
    )
