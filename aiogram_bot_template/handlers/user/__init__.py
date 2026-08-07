from aiogram import Router
from aiogram.filters import Command, CommandStart

from aiogram_bot_template import states as states
from aiogram_bot_template.filters import AdminFilter, BannedFilter, ChatTypeFilter, TextFilter as TextFilter

from . import item, unban, ban, coin, profile, shop, start, promote
from aiogram_bot_template.keyboards.inline.callbacks import Action, ShopAction


def prepare_router() -> Router:
    user_router = Router()
    user_router.message.filter(ChatTypeFilter("private"))
    user_router.message.filter(BannedFilter())

    user_router.message.register(start.menu, CommandStart())
    user_router.message.register(item.item, Command("item"), AdminFilter())
    user_router.message.register(ban.ban, Command("ban"), AdminFilter())
    user_router.message.register(unban.unban, Command("unban"), AdminFilter())
    user_router.message.register(promote.promote, Command("promote"), AdminFilter())
    user_router.callback_query.register(
        profile.profile,
        Action.filter(),
        lambda _callback, callback_data: getattr(callback_data, "action", None) == "profile",
    )
    user_router.callback_query.register(
        start.menu_callback,
        Action.filter(),
        lambda _callback, callback_data: getattr(callback_data, "action", None) == "menu",
    )
    user_router.callback_query.register(
        coin.coin,
        Action.filter(),
        lambda _callback, callback_data: getattr(callback_data, "action", None) == "coin",
    )
    user_router.callback_query.register(
        shop.shop,
        Action.filter(),
        lambda _callback, callback_data: getattr(callback_data, "action", None) == "shop",
    )
    user_router.callback_query.register(
        shop.shop_callback,
        ShopAction.filter(),
    )

    return user_router
