from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter

from aiogram_bot_template import states
from aiogram_bot_template.filters import AdminFilter, BannedFilter, ChatTypeFilter, TextFilter

from . import ban, coin, profile, start


def prepare_router() -> Router:
    user_router = Router()
    user_router.message.filter(ChatTypeFilter("private"))
    user_router.message.filter(BannedFilter())

    user_router.message.register(start.start, CommandStart())
    user_router.message.register(profile.profile, Command("profile"))
    user_router.message.register(coin.coin, Command("coin"))
    user_router.message.register(ban.ban, Command("ban"), AdminFilter())
    user_router.message.register(
        start.start,
        TextFilter("🏠В главное меню"),  # noqa: RUF001
        StateFilter(states.user.UserMainMenu.menu),
    )

    return user_router
