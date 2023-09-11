from random import shuffle
from typing import Union, Callable

from aiogram.types import Message, CallbackQuery

from loader import dp, _
from utils.post.settings import PostSettings
from states.post_settings import PostContentSettings
from messages.post import get_asking_for_url_buttons_text
from keyboards.inline.post.in_queue import get_posts_in_queue_keyboard
from keyboards.inline.post.content import get_url_buttons_keyboard_from_
from keyboards.inline.callback_data import (
    get_keyboard_with_back_inline_button_by_,
)

from .. import constants
from ..channels import get_channels


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


async def add_watermark_to_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Adds watermark to posts in queue."""
    await callback_query.answer(_("Soon..."))


async def disable_web_page_preview_for_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Disables web page preview for posts in queue."""
    constants.post_content.settings.disable_web_page_preview = (
        not constants.post_content.settings.disable_web_page_preview
    )
    await callback_query.message.edit_reply_markup(
        reply_markup=get_posts_in_queue_keyboard(
            constants.post_content.settings
        )
    )


async def disable_notification_for_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Disables notification for posts in queue."""
    constants.post_content.settings.disable_notification = (
        not constants.post_content.settings.disable_notification
    )
    await callback_query.message.edit_reply_markup(
        reply_markup=get_posts_in_queue_keyboard(
            constants.post_content.settings
        )
    )


async def shuffle_posts_in_queue(callback_query: CallbackQuery) -> None:
    """Shuffles posts in queue."""
    if not constants.post_content.settings.shuffle:
        shuffle(constants.post_content.content)
        constants.post_content.settings.shuffle = True
        await callback_query.message.edit_reply_markup(
            reply_markup=get_posts_in_queue_keyboard(
                constants.post_content.settings
            )
        )
    else:
        await callback_query.answer(_("Posts are already shuffled."))
