import secrets
from datetime import datetime, timezone
from typing import cast, TYPE_CHECKING

from aiogram.types import CallbackQuery

from aiogram_bot_template.db.user_db import get_user, give_user_coins

if TYPE_CHECKING:
    from asyncpg import Pool


async def coin(callback: CallbackQuery, **kwargs: object) -> None:
    from_user = callback.from_user

    amount = secrets.randbelow(6) + 5
    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        return

    pool = cast("Pool", db_pool)
    user_row = await get_user(pool, from_user.id)
    now = datetime.now(timezone.utc)
    cooldown_until: datetime | None = None
    if isinstance(user_row, dict):
        cooldown_value = user_row.get("coins_cooldown")
        if isinstance(cooldown_value, datetime):
            cooldown_until = cooldown_value

    if cooldown_until is not None and cooldown_until > now:
        remaining_seconds = int((cooldown_until - now).total_seconds())
        hours, remainder = divmod(remaining_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        await callback.answer(
            f"Вы сможете получить монеты снова через {hours} ч {minutes} мин {seconds} сек.⏳",
            show_alert=True,
        )
        return

    cooldown_until = datetime.fromtimestamp(int(now.timestamp()) + 3600, tz=timezone.utc)

    await give_user_coins(pool, from_user.id, amount, cooldown_until)
    await callback.answer(f"Вы получили {amount} монет! 🎉", show_alert=True)
