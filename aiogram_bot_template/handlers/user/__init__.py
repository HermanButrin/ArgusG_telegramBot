from aiogram import Router
from aiogram.filters import Command, CommandStart

from aiogram_bot_template import states as states
from aiogram_bot_template.filters import (
    AdminFilter,
    BannedFilter,
    ChatTypeFilter,
    TextFilter as TextFilter,
)

from . import (
    ban_handler,
    coin_handler,
    item_handler,
    menu_handler,
    profile_handler,
    promote_handler,
    shop_handler,
    unban_handler,
    musician_handler,
)
from aiogram_bot_template.keyboards.inline.callbacks import Action, ShopAction


def prepare_router() -> Router:
    user_router = Router()
    user_router.message.filter(ChatTypeFilter("private"))
    user_router.message.filter(BannedFilter())

    user_router.message.register(menu_handler.menu, CommandStart())
    user_router.message.register(item_handler.item, Command("item"), AdminFilter())
    user_router.message.register(ban_handler.ban, Command("ban"), AdminFilter())
    user_router.message.register(unban_handler.unban, Command("unban"), AdminFilter())
    user_router.message.register(
        promote_handler.promote, Command("promote"), AdminFilter()
    )
    user_router.callback_query.register(
        musician_handler.musician,
        Action.filter(),
        lambda _callback, callback_data: getattr(callback_data, "action", None)
        == "musician",
    )
    user_router.callback_query.register(
        musician_handler.inventory,
        Action.filter(),
        lambda _callback, callback_data: getattr(callback_data, "action", None)
        == "inventory",
    )
    user_router.callback_query.register(
        profile_handler.profile,
        Action.filter(),
        lambda _callback, callback_data: getattr(callback_data, "action", None)
        == "profile",
    )
    user_router.callback_query.register(
        menu_handler.menu_callback,
        Action.filter(),
        lambda _callback, callback_data: getattr(callback_data, "action", None)
        == "menu",
    )
    user_router.callback_query.register(
        coin_handler.coin,
        Action.filter(),
        lambda _callback, callback_data: getattr(callback_data, "action", None)
        == "coin",
    )
    user_router.callback_query.register(
        shop_handler.shop,
        Action.filter(),
        lambda _callback, callback_data: getattr(callback_data, "action", None)
        == "shop",
    )
    user_router.callback_query.register(
        shop_handler.shop_callback,
        ShopAction.filter(),
    )

    return user_router
