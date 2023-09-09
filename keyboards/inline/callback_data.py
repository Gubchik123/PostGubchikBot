from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


timezone_callback_data = CallbackData("timezone", "level", "country", "city")

subscription_callback_data = CallbackData("subscription", "level", "price")

admin_subscription_callback_data = CallbackData(
    "admin_subscription", "level", "price"
)

channel_callback_data = CallbackData("channel", "level", "channel_title")

group_callback_data = CallbackData("group", "group_name")

post_callback_data = CallbackData("post", "level", "channel_title")

post_content_callback_data = CallbackData(
    "post_content", "level", "content_index"
)

posts_in_queue_callback_data = CallbackData("posts_in_queue", "level", "date")

post_editing_callback_data = CallbackData("post_editing", "level", "post_id")


def get_back_inline_button_by_(callback_data: str) -> InlineKeyboardButton:
    """Returns back button by the given callback data."""
    return InlineKeyboardButton(text="🔙 Back", callback_data=callback_data)


def get_keyboard_with_back_inline_button_by_(
    callback_data: str,
) -> InlineKeyboardMarkup:
    """Returns keyboard with back button by the given callback data."""
    return InlineKeyboardMarkup().add(
        get_back_inline_button_by_(callback_data)
    )
