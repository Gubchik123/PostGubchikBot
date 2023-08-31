from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from loader import _


def get_menu_keyboard(has_channels: bool) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            text=_("⭐️ Subscription"), callback_data="subscription"
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Add channel"), callback_data="add_channel"
        )
    )
    if has_channels:
        keyboard.add(
            InlineKeyboardButton(
                text=_("Remove channel"), callback_data="add_channel"
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text=_("Create post"), callback_data="create_post"
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text=_("Posts in queue"), callback_data="posts_in_queue"
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Change timezone"), callback_data="change_timezone"
        )
    )
    return keyboard


def get_back_to_menu_inline_button() -> InlineKeyboardButton:
    """Returns back to menu inline button."""
    return InlineKeyboardButton(text=_("🔙 Back"), callback_data="menu")
