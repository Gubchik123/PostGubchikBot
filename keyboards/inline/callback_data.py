from aiogram.types import InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


timezone_callback_data = CallbackData("timezone", "level", "country", "city")

subscription_callback_data = CallbackData("subscription", "level", "price")

admin_subscription_callback_data = CallbackData(
    "admin_subscription", "level", "price"
)

channel_callback_data = CallbackData("channel", "level", "channel_title")


def get_back_inline_button_by_(callback_data: str) -> InlineKeyboardButton:
    """Returns back button by the given callback data."""
    return InlineKeyboardButton(text="🔙 Back", callback_data=callback_data)
