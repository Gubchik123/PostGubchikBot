from aiogram.types import CallbackQuery, Message

from loader import dp, _
from handlers.users.post import constants
from states.post_settings import PostContentSettings
from messages.post import get_asking_for_url_buttons_text
from keyboards.inline.post.content import get_url_buttons_keyboard_from_
from keyboards.inline.callback_data import (
    get_keyboard_with_back_inline_button_by_,
)

from .ask import ask_for_what_to_add_to_posts_in_queue


async def ask_for_url_buttons_to_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Adds url buttons to posts in queue."""
    await callback_query.message.edit_text(
        text=get_asking_for_url_buttons_text(),
        reply_markup=get_keyboard_with_back_inline_button_by_(
            callback_data="posts_in_queue:ask_for_what_to_add:None"
        ),
    )
    await PostContentSettings.reply_markup.set()


@dp.message_handler(state=PostContentSettings.reply_markup)
async def add_url_buttons_to_posts_in_queue(message: Message) -> None:
    """Adds url buttons to posts in queue."""
    constants.post_content.settings.reply_markup = (
        get_url_buttons_keyboard_from_(message.text)
    )
    await ask_for_what_to_add_to_posts_in_queue(message)
