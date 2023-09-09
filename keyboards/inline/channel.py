from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import _
from utils.db.models import Channel
from .menu import get_back_to_menu_inline_button
from .callback_data import (
    channel_callback_data,
    get_back_inline_button_by_,
)


def _get_new_callback_data(level: int, channel_title="None") -> str:
    """Returns new subscription callback data by the given parameters."""
    return channel_callback_data.new(level=level, channel_title=channel_title)


def get_channels_keyboard(
    all_channels: list[Channel],
) -> InlineKeyboardMarkup:
    """Returns inline keyboard with channels and back button."""
    CURRENT_LEVEL = 0

    keyboard = InlineKeyboardMarkup(row_width=1)

    for channel in all_channels:
        keyboard.add(
            InlineKeyboardButton(
                text=channel.title,
                callback_data=_get_new_callback_data(
                    CURRENT_LEVEL + 1, channel.title
                ),
            )
        )
    keyboard.add(get_back_to_menu_inline_button())
    return keyboard


def get_confirmation_keyboard(channel_title: str):
    """Returns inline keyboard with confirmation and back button."""
    CURRENT_LEVEL = 1

    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text=_("Remove"),
            callback_data=_get_new_callback_data(
                CURRENT_LEVEL + 1, channel_title
            ),
        ),
        get_back_inline_button_by_(
            callback_data=_get_new_callback_data(CURRENT_LEVEL - 1)
        ),
    )
