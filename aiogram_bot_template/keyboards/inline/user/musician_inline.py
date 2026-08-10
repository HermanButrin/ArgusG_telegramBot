from aiogram.types import InlineKeyboardMarkup

from aiogram_bot_template.keyboards.inline.consts import InlineConstructor
from aiogram_bot_template.keyboards.inline.callbacks import Action


def create_musician_menu() -> InlineKeyboardMarkup:
    return InlineConstructor.create_keyboard(
        [
            {"text": "Концерт", "callback_data": Action(action="concert")},
            {"text": "Статистика", "callback_data": Action(action="statistics")},
            {"text": "Инвентарь", "callback_data": Action(action="inventory")},
            {"text": "◀️ Назад", "callback_data": Action(action="menu")},
        ],
        [2, 1, 1],
    )
