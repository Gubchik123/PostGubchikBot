import string
import random
from datetime import datetime

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from states.post import Post
from loader import dp, scheduler, _
from utils.db.crud.user import get_user_by_
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
    post_id = _schedule_job_to_publish_user_post(
        user_chat_id=message.from_user.id,
        run_date=datetime.today().replace(hour=int(hour), minute=int(minute)),
    )
    await message.answer(
        text=_get_postpone_success_message_by_(post_id, message.text)
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
    post_id = _schedule_job_to_publish_user_post(
        user_chat_id=message.from_user.id,
        run_date=datetime.strptime(message.text, "%d.%m.%Y %H:%M"),
    )
    await message.answer(
        text=_get_postpone_success_message_by_(post_id, message.text)
    )
    await show_menu(message)


@dp.message_handler(state=(Post.time, Post.deletion_time))
async def send_message_about_wrong_date_and_time(message: Message) -> None:
    """Sends a message about wrong date and time."""
    await message.answer(
        text=_(
            "Wrong date and (or) time format. Try again!\n"
            "Format example - 15.08.2023 13:40"
        )
    )


def _schedule_job_to_publish_user_post(
    user_chat_id: int, run_date: datetime
) -> str:
    """Schedules job to publish user post
    on the given date and return generated post id."""
    user = get_user_by_(user_chat_id)
    id = generate_random_id()
    scheduler.add_job(
        publish_user_post,
        "date",
        run_date=run_date,
        id=f"{user_chat_id}_post_{id}",
        kwargs={
            "author_chat_id": user.chat_id,
            "author_language_code": user.language_code,
            "post_content": post_content,
            "selected_channels": selected_channels,
        },
    )
    return id


def generate_random_id(length: int = 12) -> str:
    """Generates random id with ascii letters and digits and returns it."""
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


def _get_postpone_success_message_by_(post_id: str, date: str) -> str:
    """Returns postpone success message by the given post id and date."""
    return _(
        "🚀 Post is scheduled! #{post_id}\n\n"
        "Selected channels: {selected_channels}\n\n"
        "Publication time: {date}"
    ).format(
        post_id=post_id,
        selected_channels=", ".join(selected_channels),
        date=date,
    )
