from datetime import datetime, timezone, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from aiogram import html, types
from aiogram.types import CallbackQuery

from aiogram_bot_template.db.user_db import get_user
from aiogram_bot_template.keyboards.inline.user.back_inline import create_back


def _format_timestamp(value: datetime | None, timezone_name: str) -> str:
    if value is None:
        return "—"

    try:
        user_tz: tzinfo = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        user_tz = timezone.utc

    aware_value = value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    return aware_value.astimezone(user_tz).strftime("%Y-%m-%d %H:%M:%S")


async def profile(callback: CallbackQuery, **kwargs: object) -> None:
    if not isinstance(callback.message, types.Message):
        await callback.answer()
        return

    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        await callback.answer("База данных недоступна.", show_alert=True)
        return

    from_user = callback.from_user
    user_row = await get_user(db_pool, from_user.id)

    if user_row is None:
        await callback.answer(
            "Профиль пока не найден. Сначала нажмите /start, чтобы сохранить пользователя.",
        )
        return

    full_name = from_user.full_name
    tag = from_user.username or "—"
    timezone_name = "Europe/Berlin"

    created_at_value = user_row.get("created_at")
    updated_at_value = user_row.get("updated_at")
    last_active_at_value = user_row.get("last_active_at")

    created_at = _format_timestamp(
        created_at_value if isinstance(created_at_value, datetime) else None,
        timezone_name,
    )
    updated_at = _format_timestamp(
        updated_at_value if isinstance(updated_at_value, datetime) else None,
        timezone_name,
    )
    last_active_at = _format_timestamp(
        last_active_at_value if isinstance(last_active_at_value, datetime) else None,
        timezone_name,
    )

    await callback.message.edit_text(
        "\n".join(
            [
                f"Имя: {html.quote(full_name)}",
                f"Тег: @{html.quote(tag)}" if tag != "—" else f"Тег: {tag}",
                f"Баланс: {user_row.get('coins')}",
                f"Аккаунт создан: {created_at}",
                f"Обновлен: {updated_at}",
                f"Последняя активность: {last_active_at}",
            ],
        ),
        reply_markup=create_back("menu"),
    )
    await callback.answer()
