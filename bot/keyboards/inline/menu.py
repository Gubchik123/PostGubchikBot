from typing import Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from loader import _


def get_menu_keyboard(has_channels: bool) -> InlineKeyboardMarkup:
    """Returns menu navigation keyboard."""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        InlineKeyboardButton(
            text=_("⭐️ Subscription"), callback_data="subscription"
        )
    )
    keyboard.insert(
        InlineKeyboardButton(text=_("👥 Referrals"), callback_data="referrals")
    )
    keyboard.insert(
        InlineKeyboardButton(
            text=_("Add channel"), callback_data="add_channel"
        )
    )
    if has_channels:
        keyboard.insert(
            InlineKeyboardButton(
                text=_("Remove channel"), callback_data="remove_channel"
            )
        )
        keyboard.insert(
            InlineKeyboardButton(
                text=_("Create post"), callback_data="create_post"
            )
        )
        keyboard.insert(
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


def get_back_to_menu_inline_button(
    btn_text: Optional[str] = None,
) -> InlineKeyboardButton:
    """Returns back to menu inline button."""
    return InlineKeyboardButton(
        text=_("🔙 Back") if btn_text is None else btn_text,
        callback_data="menu",
    )


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Returns back to menu keyboard."""
    return InlineKeyboardMarkup().add(get_back_to_menu_inline_button())
