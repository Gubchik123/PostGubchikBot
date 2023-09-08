from typing import Callable

from aiogram.types import CallbackQuery

from loader import dp, _
from utils.db.crud.user import get_user_channels_by_
from utils.db.channel_crud import remove_channel_by_
from keyboards.inline.callback_data import channel_callback_data
from keyboards.inline.channel import (
    get_channels_keyboard,
    get_confirmation_keyboard,
)

from ..commands.menu import show_menu


@dp.callback_query_handler(text="remove_channel")
async def get_channels(query: CallbackQuery, *args) -> None:
    """Shows channels to choose from to remove."""
    channels = get_user_channels_by_(query.from_user.id)
    await query.message.edit_text(
        text=_("Choose channel to remove:"),
        reply_markup=get_channels_keyboard(channels),
    )


async def confirm_channel_removal(
    query: CallbackQuery, channel_title: str
) -> None:
    """Confirms channel removal."""
    await query.message.edit_text(
        text=_(
            "Are you sure you want to remove the '{channel_title}'?"
        ).format(channel_title=channel_title),
        reply_markup=get_confirmation_keyboard(channel_title),
    )


async def remove_channel(query: CallbackQuery, channeL_title: str) -> None:
    """Removes channel."""
    remove_channel_by_(channeL_title)
    await query.answer(text=_("Channel '{}' removed.").format(channeL_title))
    await show_menu(query)


@dp.callback_query_handler(channel_callback_data.filter())
async def navigate(query: CallbackQuery, callback_data: dict) -> None:
    """Catches all other channel callback data to navigate."""
    current_level = callback_data.get("level")
    channel_title = callback_data.get("channel_title")

    current_level_function: Callable = {
        "0": get_channels,
        "1": confirm_channel_removal,
        "2": remove_channel,
    }.get(current_level)

    await current_level_function(query, channel_title)
