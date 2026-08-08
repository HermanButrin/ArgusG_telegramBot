from aiogram.types import InlineKeyboardMarkup

from aiogram_bot_template.keyboards.inline.consts import InlineConstructor
from aiogram_bot_template.keyboards.inline.callbacks import Action


def create_back(action: str = "menu", text: str = "◀️Назад") -> InlineKeyboardMarkup:
    return InlineConstructor.create_keyboard(
        [{"text": text, "callback_data": Action(action=action)}],
        [1],
    )
