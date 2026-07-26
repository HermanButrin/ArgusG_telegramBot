import asyncpg
from aiogram.filters import BaseFilter
from aiogram.types import Message

from aiogram_bot_template.data import config


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if message.from_user is None:
            return False

        pool = await asyncpg.create_pool(config.PG_LINK, min_size=1, max_size=1)
        try:
            user_row = await pool.fetchrow(
                'SELECT is_admin FROM "user_profile" WHERE telegram_id = $1',
                message.from_user.id,
            )
            if user_row is None:
                return False
            return bool(user_row["is_admin"])
        finally:
            await pool.close()
