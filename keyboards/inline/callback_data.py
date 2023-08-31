from aiogram.types import InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


timezone_callback_data = CallbackData("timezone", "level", "country", "city")


def get_back_inline_button_by_(callback_data: str) -> InlineKeyboardButton:
    """Returns back button by the given callback data."""
    return InlineKeyboardButton(text="🔙 Back", callback_data=callback_data)
