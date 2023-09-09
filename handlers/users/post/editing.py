from datetime import datetime
from typing import Callable, Optional

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from states.post import Post
from loader import dp, scheduler, _
from utils.scheduler import (
    get_user_scheduled_post_job_by_,
    get_user_scheduled_post_jobs_by_,
)
from keyboards.inline.callback_data import (
    post_editing_callback_data,
    get_keyboard_with_back_inline_button_by_,
)
from keyboards.inline.post.editing import (
    get_user_posts_keyboard,
    get_user_post_keyboard,
    get_confirmation_keyboard,
)

from .channels import get_channels
from .postponing import send_message_about_wrong_date_and_time


current_post_id = None


@dp.callback_query_handler(text="edit_post")
async def get_scheduled_user_posts(query: CallbackQuery) -> None:
    """Sends scheduled user posts to choose from to edit them."""
    user_chat_id = query.from_user.id
    user_scheduled_post_jobs = get_user_scheduled_post_jobs_by_(user_chat_id)
    if not user_scheduled_post_jobs:
        await query.answer(
            text=_("You don't have any scheduled posts yet :("),
            show_alert=True,
        )
        return
    await query.message.edit_text(
        text=_("Select a post to edit it:"),
        reply_markup=get_user_posts_keyboard(user_scheduled_post_jobs),
    )


async def get_user_post(data: Message | CallbackQuery, post_id: str) -> None:
    """
    Shows or sends post info depending on the given data (message or query).
    """
    user_scheduled_post_job = get_user_scheduled_post_job_by_(
        post_id, data.from_user.id
    )
    answer_function: Callable = (
        data.message.edit_text
        if isinstance(data, CallbackQuery)
        else data.answer
    )
    await answer_function(
        text=_(
            "Scheduled post #{post_id}\n"
            "Publication time: {run_date}\n\n"
            "You can choose an action for this post:"
        ).format(
            post_id=post_id,
            run_date=user_scheduled_post_job.next_run_time.strftime(
                "%d.%m.%Y %H:%M"
            ),
        ),
        reply_markup=get_user_post_keyboard(post_id),
    )


async def ask_for_new_publication_time(
    query: CallbackQuery, post_id: str
) -> None:
    """
    Sends message to ask for new publication time and waits (state) for it.
    """
    global current_post_id
    current_post_id = post_id
    await query.message.edit_text(
        text=_(
            "<b>Enter a new time for the scheduled post</b>\n\n"
            "Format example - 15.08.2023 13:40"
        ),
        reply_markup=get_keyboard_with_back_inline_button_by_(
            callback_data=f"post_editing:get_post:{post_id}"
        ),
    )
    await Post.new_time.set()


@dp.message_handler(
    regexp=r"^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$", state=Post.new_time
)
async def change_post_publication_time(
    message: Message, state: FSMContext
) -> None:
    """Changes post publication time and sends success message."""
    await state.finish()
    scheduler.reschedule_job(
        job_id=f"{message.from_user.id}_post_{current_post_id}",
        trigger="date",
        run_date=datetime.strptime(message.text, "%d.%m.%Y %H:%M"),
    )
    await message.reply(
        text=_(
            "😌 The publication time of the post has been changed successfully!\n\n"
            "New publication time: {run_date}"
        ).format(run_date=message.text),
    )
    await get_user_post(message, current_post_id)


@dp.message_handler(state=Post.new_time)
async def send_message_about_wrong_date(message: Message) -> None:
    """Sends a message about wrong date and time."""
    await send_message_about_wrong_date_and_time(message)


async def confirm_post_removing(query: CallbackQuery, post_id: str) -> None:
    """Sends post removing confirmation message."""
    await query.message.edit_text(
        text=_(
            "Are you sure you want to remove this post (#{post_id})?"
        ).format(post_id=post_id),
        reply_markup=get_confirmation_keyboard(post_id),
    )


async def remove_post(query: CallbackQuery, post_id: str) -> None:
    """Removes post and sends success message."""
    user_chat_id = query.from_user.id
    scheduler.remove_job(f"{user_chat_id}_post_{post_id}")
    user_scheduled_post_jobs_count = len(
        get_user_scheduled_post_jobs_by_(user_chat_id)
    )
    await query.answer(
        text=_("Post #{post_id} has been removed!").format(post_id=post_id)
    )
    await get_scheduled_user_posts(
        query
    ) if user_scheduled_post_jobs_count > 1 else await get_channels(query)


@dp.callback_query_handler(post_editing_callback_data.filter(), state="*")
async def navigate(
    query: CallbackQuery,
    callback_data: dict,
    state: Optional[FSMContext] = None,
) -> None:
    """Catches all other post editing callback data to navigate."""
    if state:
        await state.finish()
    current_level_function: Callable = {
        "get_post": get_user_post,
        "change_post_publication_time": ask_for_new_publication_time,
        "confirm_post_removing": confirm_post_removing,
        "remove_post": remove_post,
    }.get(callback_data.get("level"))

    await current_level_function(query, callback_data.get("post_id"))
