from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import asyncpg
from aiogram import html, types

from aiogram_bot_template.data import config


def _format_timestamp(value: datetime | None, timezone_name: str) -> str:
    if value is None:
        return "—"

    try:
        user_tz = ZoneInfo(timezone_name)
    except Exception:
        user_tz = timezone.utc

    if value.tzinfo is None:
        aware_value = value.replace(tzinfo=timezone.utc)
    else:
        aware_value = value

    return aware_value.astimezone(user_tz).strftime("%Y-%m-%d %H:%M:%S")


async def profile(msg: types.Message) -> None:
    if msg.from_user is None:
        return

    pool = await asyncpg.create_pool(config.PG_LINK, min_size=1, max_size=1)
    try:
        user_row = await pool.fetchrow(
            """
            SELECT
                first_name,
                last_name,
                username,
                coins,
                level,
                xp,
                created_at,
                updated_at,
                last_active_at
            FROM "user"
            WHERE telegram_id = $1
            """,
            msg.from_user.id,
        )

        if user_row is None:
            await msg.answer(
                "Профиль пока не найден. Сначала нажмите /start, чтобы сохранить пользователя.",
            )
            return

        full_name = " ".join(
            part for part in [user_row["first_name"], user_row["last_name"]] if part
        ).strip()
        if not full_name:
            full_name = msg.from_user.full_name

        tag = user_row["username"] or "—"
        timezone_name = "Europe/Moscow"
        created_at = _format_timestamp(user_row["created_at"], timezone_name)
        updated_at = _format_timestamp(user_row["updated_at"], timezone_name)
        last_active_at = _format_timestamp(user_row["last_active_at"], timezone_name)

        await msg.answer(
            "\n".join(
                [
                    f"Имя: {html.quote(full_name)}",
                    f"Тег: @{html.quote(tag)}" if tag != "—" else f"Тег: {tag}",
                    f"Coins: {user_row['coins']}",
                    f"Level: {user_row['level']}",
                    f"XP: {user_row['xp']}",
                    f"Created at: {created_at}",
                    f"Updated at: {updated_at}",
                    f"Last active at: {last_active_at}",
                ],
            ),
        )
    finally:
        await pool.close()
