from aiogram.types import CallbackQuery

import secrets
from datetime import datetime, timezone


from aiogram_bot_template.db.user import award_user_coins


async def coin(callback: CallbackQuery, **kwargs: object) -> None:
    if callback.from_user is None:
        return

    amount = secrets.randbelow(6) + 5
    db_pool = kwargs.get("db_pool")
    if db_pool is None:
        return

    user_row = kwargs.get("user")
    now = datetime.now(timezone.utc)
    cooldown_until = None
    if isinstance(user_row, dict):
        cooldown_until = user_row.get("coins_cooldown")

    if cooldown_until is not None and cooldown_until > now:
        remaining_seconds = int((cooldown_until - now).total_seconds())
        hours, remainder = divmod(remaining_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        await callback.answer(
            f"Вы сможете получить монеты снова через {hours} ч {minutes} мин {seconds} сек.⏳",
            show_alert=True,
        )
        return

    cooldown_until = now.fromtimestamp(int(now.timestamp()) + 3600, tz=timezone.utc)

    await award_user_coins(db_pool, callback.from_user.id, amount, cooldown_until)
    await callback.answer(f"Вы получили {amount} монет! 🎉", show_alert=True)
