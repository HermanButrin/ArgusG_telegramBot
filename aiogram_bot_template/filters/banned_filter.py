import asyncpg
from aiogram.filters import BaseFilter
from aiogram.types import Message

from aiogram_bot_template.db.user_db import is_user_not_banned


class BannedFilter(BaseFilter):
    async def __call__(
        self,
        message: Message,
        db_pool: asyncpg.Pool | None = None,
    ) -> bool:
        if message.from_user is None or db_pool is None:
            return True

        return await is_user_not_banned(db_pool, message.from_user.id)
