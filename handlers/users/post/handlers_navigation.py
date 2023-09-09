from typing import Callable

from aiogram.types import CallbackQuery

from loader import dp
from keyboards.inline.callback_data import post_callback_data

from .channels import (
    select_or_remove_channel,
    ask_for_group_name,
    ask_for_post_content,
    ask_for_post_album,
)
from .publishing_with_deletion import (
    ask_for_deletion_time,
    publish_post_with_deletion,
)
from .publishing import publish_post
from .postponing import postpone_post


@dp.callback_query_handler(post_callback_data.filter(), state="*")
async def navigate(callback_query: CallbackQuery, callback_data: dict) -> None:
    """Catches all other post callback data to navigate."""
    current_level_function: Callable = {
        "select_or_remove_channel": select_or_remove_channel,
        "create_group": ask_for_group_name,
        "ask_for_post_content": ask_for_post_content,
        "ask_for_post_album": ask_for_post_album,
        "ask_for_deletion_time": ask_for_deletion_time,
        "publish_post_with_deletion": publish_post_with_deletion,
        "publish_post": publish_post,
        "postpone_post": postpone_post,
    }.get(callback_data.get("level"))

    await current_level_function(
        callback_query, callback_data.get("channel_title")
    )
