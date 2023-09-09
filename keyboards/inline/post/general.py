from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import _
from utils.db.models import Channel, Group

from ..menu import get_back_to_menu_inline_button
from ..callback_data import (
    post_callback_data,
    get_back_inline_button_by_,
)


def _get_new_callback_data(level: str, channel_title="None") -> str:
    """Returns new post callback data by the given parameters."""
    return post_callback_data.new(level=level, channel_title=channel_title)


def get_channels_keyboard(
    all_channels: list[Channel],
    all_groups: list[Group],
    selected_channels: list[str],
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)

    for channel in all_channels:
        mark = "✅" if channel.title in selected_channels else ""
        keyboard.insert(
            InlineKeyboardButton(
                text=mark + channel.title,
                callback_data=_get_new_callback_data(
                    "select_or_remove_channel",
                    channel.title,
                ),
            )
        )
    keyboard.row()
    for group in all_groups:
        keyboard.insert(
            InlineKeyboardButton(
                text=f"Group: {group.name}",
                callback_data=f"group:{group.name}",
            )
        )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Select all"),
            callback_data=_get_new_callback_data(
                "select_or_remove_channel", "all"
            ),
        )
    )
    if selected_channels:
        keyboard.add(
            InlineKeyboardButton(
                text=_("Next"),
                callback_data=_get_new_callback_data("ask_for_post_content"),
            )
        )
        if len(selected_channels) > 1:
            keyboard.insert(
                InlineKeyboardButton(
                    text=_("Create group"),
                    callback_data=_get_new_callback_data("create_group"),
                )
            )
    else:
        keyboard.add(
            InlineKeyboardButton(
                text=_("Scheduled posts"), callback_data="edit_post"
            )
        )
    keyboard.add(get_back_to_menu_inline_button())
    return keyboard


def get_post_album_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            text=_("Create an album"),
            callback_data=_get_new_callback_data("ask_for_post_album"),
        )
    )


def get_pre_publish_keyboard() -> InlineKeyboardMarkup:
    """Returns pre publish keyboard."""
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text=_("Publish but set a deletion timer"),
            callback_data=_get_new_callback_data("ask_for_deletion_time"),
        ),
        InlineKeyboardButton(
            text=_("Publish"),
            callback_data=_get_new_callback_data("publish_post"),
        ),
        InlineKeyboardButton(
            text=_("Postpone"),
            callback_data=_get_new_callback_data("postpone_post"),
        ),
        get_back_to_menu_inline_button(_("Cancel")),
    )


def get_deletion_hours_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=3)
    for hour in (1, 3, 6, 9, 12, 15, 18, 21, 24):
        keyboard.insert(
            InlineKeyboardButton(
                text=str(hour),
                callback_data=_get_new_callback_data(
                    "publish_post_with_deletion", str(hour)
                ),
            )
        )
    keyboard.add(
        get_back_inline_button_by_(callback_data="time_to_publish_post")
    )
    return keyboard
