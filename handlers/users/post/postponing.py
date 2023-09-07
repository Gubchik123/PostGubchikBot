from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from states.post import Post
from loader import dp, scheduler, _
from utils.db.user_crud import get_user_by_
from utils.scheduler import publish_user_post
from keyboards.inline.callback_data import (
    get_keyboard_with_back_inline_button_by_,
)

from ..commands.menu import show_menu
from .constants import post_content, selected_channels


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


@dp.message_handler(regexp=r"^\d{2}:\d{2}$", state=Post.time)
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
