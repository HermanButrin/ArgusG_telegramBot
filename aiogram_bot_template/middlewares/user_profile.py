from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from aiogram_bot_template.db.user import fetch_user_profile


class UserProfileMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Update):
            return await handler(event, data)

        user = None
        if event.message is not None and event.message.from_user is not None:
            user = event.message.from_user
        elif event.callback_query is not None and event.callback_query.from_user is not None:
            user = event.callback_query.from_user
        elif event.edited_message is not None and event.edited_message.from_user is not None:
            user = event.edited_message.from_user

        if user is None:
            return await handler(event, data)

        db_pool = data.get("db_pool")
        if db_pool is None:
            return await handler(event, data)

        with suppress(Exception):
            user_row = await fetch_user_profile(db_pool, user.id)
            data["user_profile"] = user_row

        return await handler(event, data)
