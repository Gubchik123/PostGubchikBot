from typing import Callable, Union

from aiogram.types import CallbackQuery, Message

from loader import dp, _
from handlers.users.post import constants
from utils.post.settings import PostSettings
from handlers.users.post.channels import get_channels
from keyboards.inline.post.in_queue import get_posts_in_queue_keyboard


@dp.callback_query_handler(text="posts_in_queue")
async def get_channels_(callback_query: CallbackQuery) -> None:
    """Sends a message with inline keyboard to select a channel."""
    constants.post_content.settings = PostSettings()
    await get_channels(callback_query, target="post in queue")


async def ask_for_what_to_add_to_posts_in_queue(
    data: Union[Message, CallbackQuery],
) -> None:
    """Asks for what to add to posts in queue."""
    answer_function: Callable = (
        data.message.edit_text
        if isinstance(data, CallbackQuery)
        else data.answer
    )
    await answer_function(
        _("Select what you want to add to all posts in the queue:"),
        reply_markup=get_posts_in_queue_keyboard(
            constants.post_content.settings
        ),
    )
