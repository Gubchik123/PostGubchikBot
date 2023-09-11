from pytz import timezone
from datetime import datetime, timedelta
from typing import Union, Optional, List, Tuple, Callable

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from loader import dp, scheduler, _
from utils.db.crud.user import get_user_by_
from states.post_in_queue import PostInQueue
from utils.scheduler import publish_user_post_in_queue
from keyboards.inline.callback_data import posts_in_queue_callback_data
from keyboards.inline.post.in_queue import (
    get_posts_in_queue_keyboard,
    get_date_keyboard,
    get_time_keyboard,
    get_interval_keyboard,
)

from ..commands.menu import show_menu
from .channels import get_channels
from .postponing import generate_random_id
from .constants import selected_channels, post_content


@dp.callback_query_handler(text="posts_in_queue")
async def get_channels_(callback_query: CallbackQuery) -> None:
    """Sends a message with inline keyboard to select a channel."""
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
        reply_markup=get_posts_in_queue_keyboard(),
    )


async def add_signature_to_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Adds signature to posts in queue."""
    await callback_query.answer(_("Soon..."))


async def add_url_buttons_to_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Adds url buttons to posts in queue."""
    await callback_query.answer(_("Soon..."))


async def add_watermark_to_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Adds watermark to posts in queue."""
    await callback_query.answer(_("Soon..."))


async def remove_author_text_from_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Removes author text from posts in queue."""
    await callback_query.answer(_("Soon..."))


async def disable_web_page_preview_for_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Disables web page preview for posts in queue."""
    await callback_query.answer(_("Soon..."))


async def disable_notification_for_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Disables notification for posts in queue."""
    await callback_query.answer(_("Soon..."))


async def send_posts_in_queue_as_album(callback_query: CallbackQuery) -> None:
    """Sends posts in queue as album."""
    await callback_query.answer(_("Soon..."))


async def shuffle_posts_in_queue(callback_query: CallbackQuery) -> None:
    """Shuffles posts in queue."""
    await callback_query.answer(_("Soon..."))


start_date = ""
time = ""
interval = ""


async def ask_for_start_date_to_send_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Asks for start date to send posts-in-queue."""
    await callback_query.message.edit_text(
        text=_(
            "Send the date from which to start posting messages "
            "in the format: DD.MM.YYYY (15.08.2023)"
        ),
        reply_markup=get_date_keyboard(),
    )
    await PostInQueue.date.set()


@dp.message_handler(regexp=r"^\d{2}\.\d{2}\.\d{4}$", state=PostInQueue.date)
async def get_start_date_to_send_posts_in_queue(message: Message) -> None:
    """Gets start date to send posts-in-queue."""
    await ask_for_time_to_send_posts_in_queue(message, date_=message.text)


@dp.message_handler(state=PostInQueue.date)
async def send_message_about_wrong_date(message: Message) -> None:
    """Sends message about wrong date."""
    await message.answer(
        _("Wrong date! Try again!\n\nFormat example: 15.08.2023")
    )


async def ask_for_time_to_send_posts_in_queue(
    data: Union[Message, CallbackQuery], date_: str
) -> None:
    """Asks for time between which posts should be published and waits (state) for it."""
    global start_date
    start_date = date_
    answer_function: Callable = (
        data.message.edit_text
        if isinstance(data, CallbackQuery)
        else data.answer
    )
    await answer_function(
        text=_(
            "Enter the time between which posts should be published (for example 09:20-21:20)\n"
            "Or send the time in this format:\n"
            "12:00\n12:40\n15:00\n\n"
            "<b>Date</b>: {date}\n"
            "<b>Channel(s)</b>: {channels}\n"
        ).format(date=start_date, channels=", ".join(selected_channels)),
        reply_markup=get_time_keyboard(),
    )
    await PostInQueue.time.set()


@dp.message_handler(
    regexp=r"^\d{2}:\d{2}-\d{2}:\d{2}$", state=PostInQueue.time
)
async def get_time_to_send_posts_in_queue(message: Message) -> None:
    """Gets time to send posts-in-queue."""
    global time
    time = message.text
    await ask_for_interval_to_send_posts_in_queue(message)


@dp.message_handler(
    lambda message: "\n" in message.text, state=PostInQueue.time
)
async def get_time_to_send_posts_in_queue(message: Message) -> None:
    """Gets times to send posts-in-queue."""
    global time
    time = message.text
    await postpone_posts_in_queue(message)


@dp.message_handler(state=PostInQueue.time)
async def send_message_about_wrong_time(message: Message) -> None:
    """Sends message about wrong time."""
    await message.answer(
        _(
            "Wrong time! Try again!\n\n"
            "Format example: 09:20-21:20\n"
            "Or send the time in this format:\n"
            "12:00\n12:40\n15:00"
        )
    )


async def ask_for_interval_to_send_posts_in_queue(
    message: Message,
) -> None:
    """Asks for interval between posts in minutes and waits (state) for it."""
    time_ = (
        time.split("\n")[0] + " - " + time.split("\n")[-1]
        if "\n" in time
        else time
    )
    await message.answer(
        text=_(
            "Send the interval between posts in minutes (for example: 15)\n\n"
            "<b>Date</b>: {date}\n"
            "<b>Time</b>: {time}\n"
            "<b>Channel(s)</b>: {channels}\n"
        ).format(
            date=start_date, time=time_, channels=", ".join(selected_channels)
        ),
        reply_markup=get_interval_keyboard(start_date),
    )
    await PostInQueue.interval.set()


@dp.message_handler(regexp=r"^\d\d?$", state=PostInQueue.interval)
async def get_interval_to_send_posts_in_queue(message: Message) -> None:
    """Gets interval to send posts-in-queue."""
    global interval
    interval = int(message.text)
    await postpone_posts_in_queue(message)


@dp.message_handler(state=PostInQueue.interval)
async def send_message_about_wrong_interval(message: Message) -> None:
    """Sends message about wrong interval."""
    await message.answer(
        text=_("Wrong interval! Try again!\n\nFormat example: 15")
    )


async def postpone_posts_in_queue(message: Message) -> None:
    """Processes posts in queue."""
    await message.answer(_("Processing..."))
    user = get_user_by_(message.from_user.id)
    posts_count, publishing_times = _postpone_posts_in_queue(
        user.chat_id, user.language_code, user.timezone
    )
    await message.answer(
        _(
            "🚀 {posts_count} posts are scheduled successfully!\n\n"
            "Channel(s): {channels}\n\n"
            "Publishing times:\n{publishing_times}"
        ).format(
            posts_count=posts_count,
            channels=", ".join(selected_channels),
            publishing_times=publishing_times,
        )
    )
    await show_menu(message)


def _postpone_posts_in_queue(
    user_chat_id: int, user_language_code: str, user_timezone: str
) -> Tuple[int, str]:
    """Postpones posts in queue."""
    user_datetime_now = datetime.now(timezone(user_timezone))
    times = _get_times(user_datetime_now)
    times_count = len(times)
    publishing_times = ""
    current_time_index = 0
    posts_count = len(post_content)
    day, month, year = start_date.split(".")
    current_datetime = user_datetime_now.replace(
        year=int(year), month=int(month), day=int(day), second=0, microsecond=0
    )
    for count, post in enumerate(post_content):
        current_time = times[current_time_index]
        current_datetime = current_datetime.replace(
            hour=current_time.hour, minute=current_time.minute
        )
        _schedule_job_to_publish_user_post_in_queue(
            user_chat_id, user_language_code, post, current_datetime
        )
        publishing_times += _get_publishing_time_for_adding_to_message_by_(
            count, posts_count, current_datetime
        )
        # Check if the current time is after the end time for today
        if (
            current_datetime.hour + 1 > times[-1].hour
            and current_datetime.minute + 1 > times[-1].minute
        ):
            current_datetime += timedelta(days=1)
        current_time_index = (current_time_index + 1) % times_count
    return posts_count, publishing_times


def _get_times(user_datetime_now: datetime) -> List[datetime]:
    """Returns times between which posts should be published."""
    times = []
    if "\n" in time:
        for hour_and_minute in time.split("\n"):
            hour, minute = hour_and_minute.split(":")
            times += user_datetime_now.replace(
                hour=int(hour), minute=int(minute)
            )
    else:
        start_time, end_time = time.split("-")
        start_hour, start_minute = start_time.split(":")
        start_time = user_datetime_now.replace(
            hour=int(start_hour), minute=int(start_minute)
        )
        end_hour, end_minute = end_time.split(":")
        end_time = user_datetime_now.replace(
            hour=int(end_hour), minute=int(end_minute)
        )
        while start_time <= end_time:
            times.append(start_time)
            start_time += timedelta(minutes=interval)
    return times


def _schedule_job_to_publish_user_post_in_queue(
    user_chat_id: int,
    user_language_code: str,
    post_content_item: dict,
    run_date: datetime,
) -> None:
    """Schedules job to publish user post in queue on the given date."""
    scheduler.add_job(
        publish_user_post_in_queue,
        "date",
        run_date=run_date,
        id=f"{user_chat_id}_post_in_queue_{generate_random_id()}",
        kwargs={
            "author_chat_id": user_chat_id,
            "author_language_code": user_language_code,
            "post_content_item": post_content_item,
            "selected_channels": selected_channels,
        },
    )


def _get_publishing_time_for_adding_to_message_by_(
    count: int, posts_count: int, current_datetime: datetime
) -> bool:
    """Returns publishing time for adding to message
    by checking the given count and posts count."""
    if posts_count < 5:
        return f"{count + 1} - {current_datetime.strftime('%d.%m.%Y %H:%M')}\n"
    elif count == posts_count - 3:
        return "...\n"
    elif count in (0, 1, 2, posts_count - 2, posts_count - 1):
        return f"{count + 1} - {current_datetime.strftime('%d.%m.%Y %H:%M')}\n"
    return ""


@dp.callback_query_handler(posts_in_queue_callback_data.filter(), state="*")
async def navigate_all_other_posts_in_queue_callback_data(
    callback_query: CallbackQuery,
    callback_data: dict,
    state: Optional[FSMContext] = None,
) -> None:
    """Catches all other post callback data to navigate."""
    if state:
        await state.finish()
    current_level_function: Callable = {
        "ask_for_what_to_add": ask_for_what_to_add_to_posts_in_queue,
        # handlers to do something with posts in queue
        "add_signature": add_signature_to_posts_in_queue,
        "add_url_buttons": add_url_buttons_to_posts_in_queue,
        "add_watermark": add_watermark_to_posts_in_queue,
        "remove_author_text": remove_author_text_from_posts_in_queue,
        "disable_web_page_preview": disable_web_page_preview_for_posts_in_queue,
        "disable_notification": disable_notification_for_posts_in_queue,
        "send_posts_in_queue_as_album": send_posts_in_queue_as_album,
        "shuffle": shuffle_posts_in_queue,
        # handlers to set up posts in queue sending
        "ask_for_start_date": ask_for_start_date_to_send_posts_in_queue,
        "ask_for_time": ask_for_time_to_send_posts_in_queue,
        "ask_for_interval": ask_for_interval_to_send_posts_in_queue,
    }.get(callback_data.get("level"))

    try:
        await current_level_function(callback_query)
    except TypeError:
        await current_level_function(callback_query, callback_data.get("date"))
