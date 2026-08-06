from aiogram.types import InlineKeyboardMarkup

from aiogram_bot_template.keyboards.inline.consts import InlineConstructor
from aiogram_bot_template.keyboards.inline.callbacks import Action


def create_start_menu() -> InlineKeyboardMarkup:
    return InlineConstructor.create_keyboard(
        [
            {"text": "Магазин", "callback_data": Action(action="shop")},
            {"text": "Профиль", "callback_data": Action(action="profile")},
            {"text": "Музыкант", "callback_data": Action(action="musician")},
        ],
        [2, 1],
    )
