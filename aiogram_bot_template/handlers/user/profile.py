from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from aiogram import html, types


def _format_timestamp(value: datetime | None, timezone_name: str) -> str:
    if value is None:
        return "—"

    try:
        user_tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        user_tz = timezone.utc

    if value.tzinfo is None:
        aware_value = value.replace(tzinfo=timezone.utc)
    else:
        aware_value = value

    return aware_value.astimezone(user_tz).strftime("%Y-%m-%d %H:%M:%S")


async def profile(msg: types.Message, **kwargs: object) -> None:
    if msg.from_user is None:
        return

    user_row = kwargs.get("user")
    if not user_row:
        await msg.answer(
            "Профиль пока не найден. Сначала нажмите /start, чтобы сохранить пользователя.",
        )
        return

    full_name = " ".join(
        part for part in [user_row.get("first_name"), user_row.get("last_name")] if part
    ).strip()
    if not full_name:
        full_name = msg.from_user.full_name

    tag = user_row.get("username") or "—"
    timezone_name = "Europe/Moscow"
    created_at = _format_timestamp(user_row.get("created_at"), timezone_name)
    updated_at = _format_timestamp(user_row.get("updated_at"), timezone_name)
    last_active_at = _format_timestamp(user_row.get("last_active_at"), timezone_name)

    await msg.answer(
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
    )
