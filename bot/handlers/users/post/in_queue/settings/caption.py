from aiogram.types import CallbackQuery, Message

from loader import dp, _
from handlers.users.post import constants
from states.post_settings import PostContentSettings
from keyboards.inline.callback_data import (
    get_keyboard_with_back_inline_button_by_,
)

from .ask import ask_for_what_to_add_to_posts_in_queue


async def ask_for_caption_to_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Asks for caption to posts in queue and waits (state) for it."""
    await callback_query.message.edit_text(
        text=_("Send me new caption for all posts in the queue."),
        reply_markup=get_keyboard_with_back_inline_button_by_(
            callback_data="posts_in_queue:ask_for_what_to_add:None"
        ),
    )
    await PostContentSettings.caption.set()


@dp.message_handler(state=PostContentSettings.caption)
async def add_caption_to_posts_in_queue(message: Message) -> None:
    """Adds caption to posts in queue."""
    constants.post_content.settings.caption = message.text
    await ask_for_what_to_add_to_posts_in_queue(message)
