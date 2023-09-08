from typing import Optional
from datetime import datetime, timedelta

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from states.post import Post
from loader import dp, scheduler, _
from utils.scheduler import delete_post
from utils.db.crud.user import get_user_channels_by_
from keyboards.inline.post.general import get_deletion_hours_keyboard

from ..commands.menu import show_menu
from .constants import post_content, selected_channels
from .postponing import send_message_about_wrong_date_and_time


async def ask_for_deletion_time(query: CallbackQuery, *args) -> None:
    """Asks for deletion time and waits (state) for it."""
    await query.message.edit_text(
        text=_(
            "You can set a self-destruct timer for the post.\n\n"
            "Select or send the number of hours after which you want to delete the post.\n"
        ),
        reply_markup=get_deletion_hours_keyboard(),
    )
    await Post.deletion_time.set()


@dp.message_handler(regexp=r"^\d\d?:\d\d?$", state=Post.deletion_time)
async def check_deletion_time(message: Message, state: FSMContext) -> None:
    """Postpones the post by the given time."""
    await state.finish()
    hour, minute = message.text.split(":")
    hour, minute = int(hour), int(minute)
    if hour > 24 or hour < 1 or minute > 59 or minute < 0:
        await send_message_about_wrong_date_and_time(message)
        return
    await publish_post_with_deletion(message, hour=hour, minute=minute)


async def publish_post_with_deletion(
    data: Message | CallbackQuery, hour: str, minute: Optional[int] = 0
) -> None:
    """Publishes the post into the selected channels with deletion."""
    hour = int(hour)
    if isinstance(data, CallbackQuery):
        message = data.message
        # ! Workaround with user chat id to avoid "No channels" in the menu handler
        message.from_user.id = data.from_user.id
    else:
        message = data
    await message.answer(_("Publishing..."))
    for channel in get_user_channels_by_(message.from_user.id):
        if channel.title in selected_channels:
            await post_content.send_to_(channel.chat_id)
            _schedule_job_to_delete_post_from_channel_by_(
                channel.chat_id, hour, minute
            )
            post_content.clear_message_ids()
    await message.answer(
        text=_(
            "Published!\n\n"
            "Post will be deleted in {hour} hours and {minute} minutes."
        ).format(hour=hour, minute=minute)
    )
    post_content.clear()
    await show_menu(message)


def _schedule_job_to_delete_post_from_channel_by_(
    channel_chat_id: int, hour: int, minute: int
) -> None:
    """
    Schedules job to delete post from the channel by the given channel chat id.
    """
    scheduler.add_job(
        delete_post,
        "date",
        run_date=datetime.now() + timedelta(hours=hour, minutes=minute),
        kwargs={
            "channel_chat_id": channel_chat_id,
            "message_ids": post_content.message_ids,
        },
    )
