from random import shuffle

from aiogram.types import CallbackQuery

from loader import _
from handlers.users.post import constants
from keyboards.inline.post.in_queue import get_posts_in_queue_keyboard


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
