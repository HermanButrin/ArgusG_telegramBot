from aiogram.filters.callback_data import CallbackData


class Action(CallbackData, prefix="act"):
    action: str


class ShopAction(CallbackData, prefix="shop"):
    action: str
    instrument_type: str | None = None
    brand: str | None = None
    model: str | None = None
