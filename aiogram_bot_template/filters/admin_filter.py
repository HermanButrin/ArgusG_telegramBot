import asyncpg
from aiogram.filters import BaseFilter
from aiogram.types import Message

from aiogram_bot_template.db.user_db import is_user_admin


class AdminFilter(BaseFilter):
    async def __call__(
        self, message: Message, db_pool: asyncpg.Pool | None = None
    ) -> bool:
        if message.from_user is None or db_pool is None:
            return False

        return await is_user_admin(db_pool, message.from_user.id)
