from typing import Optional, Callable
from datetime import datetime, timedelta

from pytz import timezone
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from states.post import Post
from loader import dp, scheduler, _
from .commands.menu import show_menu
from utils.post_content import PostContent
from utils.scheduler import delete_post, publish_user_post
from utils.db.user_crud import get_user_by_, get_user_channels_by_
from keyboards.inline.post import (
    get_channels_keyboard,
    get_pre_publish_keyboard,
    get_deletion_hours_keyboard,
)
from keyboards.inline.callback_data import (
    post_callback_data,
    get_keyboard_with_back_inline_button_by_,
)


selected_channels = []
post_content = PostContent()
TIME_REGEXP = r"^\d{2}:\d{2}$"


@dp.callback_query_handler(text="create_post", state="*")
async def get_channels(
    query: CallbackQuery, state: Optional[FSMContext] = None
) -> None:
    """Sends a message with inline keyboard to select a channel."""
    if state:
        await state.finish()
    selected_channels.clear()
    await query.message.edit_text(
        text=_("Select the channel(s) you want to post to:"),
        reply_markup=get_channels_keyboard(
            get_user_channels_by_(query.from_user.id), selected_channels
        ),
    )


async def select_or_remove_channel(
    query: CallbackQuery, channel_title: str
) -> None:
    """Selects or removes the channel
    by the given channel title and updates the keyboard."""
    selected_channels.remove(
        channel_title
    ) if channel_title in selected_channels else selected_channels.append(
        channel_title
    )
    user_channels = get_user_channels_by_(query.from_user.id)
    if len(user_channels) == len(selected_channels):
        await ask_for_post_content(query)
        return
    await query.message.edit_reply_markup(
        reply_markup=get_channels_keyboard(user_channels, selected_channels)
    )


async def select_all_channels(query: CallbackQuery, *args) -> None:
    """Selects all channels and updates the keyboard."""
    selected_channels.clear()
    for channel in get_user_channels_by_(query.from_user.id):
        selected_channels.append(channel.title)
    await ask_for_post_content(query)


async def ask_for_post_content(query: CallbackQuery, *args) -> None:
    """Asks for post content and waits (state) for it."""
    post_content.clear()
    await query.message.edit_text(
        text=_(
            "You selected: {selected_channels}\n\n"
            "Send me post content (text, photo, video, gif...)\n\n"
            "To finish, send or click /stop\n"
            "To cancel, send or click /menu"
        ).format(selected_channels=", ".join(selected_channels)),
        reply_markup=get_keyboard_with_back_inline_button_by_(
            callback_data="create_post"
        ),
    )
    await Post.content.set()


@dp.message_handler(commands=["stop"], state=Post.content)
@dp.callback_query_handler(text="time_to_publish_post", state="*")
async def ask_about_time_to_publish_post(
    data: Message | CallbackQuery, state: FSMContext
) -> None:
    """Asks about time to publish the post."""
    if state:
        await state.finish()
    answer_function: Callable = (
        data.message.edit_text
        if isinstance(data, CallbackQuery)
        else data.answer
    )
    await answer_function(
        text=_(
            "Post content is ready to publish into: {selected_channels}\n\n"
            "Do you want to publish it now or later?"
        ).format(selected_channels=", ".join(selected_channels)),
        reply_markup=get_pre_publish_keyboard(),
    )


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


@dp.message_handler(regexp=TIME_REGEXP, state=Post.deletion_time)
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


async def publish_post(query: CallbackQuery, *args) -> None:
    """Publishes the post into the selected channels."""
    await query.message.answer(_("Publishing..."))
    for channel in get_user_channels_by_(query.from_user.id):
        if channel.title in selected_channels:
            await post_content.send_to_(channel.chat_id)
    await query.message.answer(_("Published!"))
    post_content.clear()
    # ! Workaround with user chat id to avoid "No channels" in the menu handler
    query.message.from_user.id = query.from_user.id
    await show_menu(query.message)


async def postpone_post(query: CallbackQuery, *args) -> None:
    """Postpones the post to publish it later."""
    await query.message.edit_text(
        text=_(
            "Send me the time to publish the post <b>today</b>.\n"
            "Send date and time to schedule post publishing for any other day.\n\n"
            "Format example (today): 15.08.2023 13:40"
        ),
        reply_markup=get_keyboard_with_back_inline_button_by_(
            callback_data="time_to_publish_post"
        ),
    )
    await Post.time.set()


@dp.message_handler(regexp=TIME_REGEXP, state=Post.time)
async def postpone_post_by_time(message: Message, state: FSMContext) -> None:
    """Postpones the post by the given time."""
    await state.finish()
    hour, minute = message.text.split(":")
    _schedule_job_to_publish_user_post(
        user_chat_id=message.from_user.id,
        run_date=datetime.today().replace(hour=int(hour), minute=int(minute)),
    )
    await message.answer(
        text=_("Post is scheduled for today at {time}").format(
            time=message.text
        ),
    )
    await show_menu(message)


@dp.message_handler(
    regexp=r"^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$", state=Post.time
)
async def postpone_post_by_date_and_time(
    message: Message, state: FSMContext
) -> None:
    """Postpones the post by the given date and time."""
    await state.finish()
    _schedule_job_to_publish_user_post(
        user_chat_id=message.from_user.id,
        run_date=datetime.strptime(message.text, "%d.%m.%Y %H:%M"),
    )
    await message.answer(
        text=_("Post is scheduled for {date}!").format(date=message.text),
    )
    await show_menu(message)


@dp.message_handler(state=(Post.time, Post.deletion_time))
async def send_message_about_wrong_date_and_time(message: Message) -> None:
    """Sends a message about wrong date and time."""
    await message.answer(
        text=_(
            "Wrong date and (or) time format. Try again!\n"
            "Time format example - 13:09\n"
            "Date and time format example - 15.08.2023 13:40"
        )
    )


@dp.callback_query_handler(post_callback_data.filter(), state="*")
async def navigate(query: CallbackQuery, callback_data: dict) -> None:
    """Catches all other post callback data to navigate."""
    current_level_function: Callable = {
        "select_or_remove_channel": select_or_remove_channel,
        "select_all_channels": select_all_channels,
        "ask_for_post_content": ask_for_post_content,
        "ask_for_deletion_time": ask_for_deletion_time,
        "publish_post_with_deletion": publish_post_with_deletion,
        "publish_post": publish_post,
        "postpone_post": postpone_post,
    }.get(callback_data.get("level"))

    await current_level_function(query, callback_data.get("channel_title"))


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


def _schedule_job_to_publish_user_post(
    user_chat_id: int, run_date: datetime
) -> None:
    """Schedules job to publish user post on the given date."""
    user = get_user_by_(user_chat_id)
    scheduler.add_job(
        publish_user_post,
        "date",
        run_date=run_date,
        kwargs={
            "author_chat_id": user.chat_id,
            "author_language_code": user.language_code,
            "post_content": post_content,
            "selected_channels": selected_channels,
        },
    )
