from aiogram.types import InlineKeyboardMarkup

from aiogram_bot_template.keyboards.inline.consts import InlineConstructor
from aiogram_bot_template.keyboards.inline.callbacks import Action


def create_start_menu() -> InlineKeyboardMarkup:
    return InlineConstructor.create_keyboard(
        [
            {"text": "Музыкант", "callback_data": Action(action="musician")},
            {"text": "Профиль", "callback_data": Action(action="profile")},
            {"text": "Магазин", "callback_data": Action(action="shop")},
            {"text": "Монетки!", "callback_data": Action(action="coin")},
        ],
        [2, 1, 1],
    )
