from apscheduler.job import Job
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import _

from ..callback_data import (
    post_editing_callback_data,
    get_back_inline_button_by_,
)


def _get_new_callback_data(
    level: str, post_type: str = "None", post_id: str = "None"
) -> str:
    """Returns new post editing callback data by the given parameters."""
    return post_editing_callback_data.new(
        level=level, post_type=post_type, post_id=post_id
    )


def get_user_posts_keyboard(
    user_scheduled_post_jobs: tuple[Job], post_type: str = "None"
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    for job in user_scheduled_post_jobs:
        post_id = job.id.split("_")[-1]  # <user_chat_id>_post_<post_id>
        keyboard.add(
            InlineKeyboardButton(
                text=_("Publication time: {run_date} [{post_id}]").format(
                    run_date=job.next_run_time.strftime("%d.%m.%Y %H:%M"),
                    post_id=post_id,
                ),
                callback_data=_get_new_callback_data(
                    "get_post", post_type, post_id
                ),
            )
        )
    if post_type == "None":
        keyboard.add(
            InlineKeyboardButton(
                text=_("Posts in queue"),
                callback_data=_get_new_callback_data("get_posts", "in_queue"),
            )
        )
    keyboard.add(get_back_inline_button_by_("create_post"))
    return keyboard


def get_user_post_keyboard(
    post_id: str, post_type: str = "None"
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=_("Change publication time"),
            callback_data=_get_new_callback_data(
                "change_time", post_type, post_id
            ),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Remove"),
            callback_data=_get_new_callback_data(
                "confirm_removing", post_type, post_id
            ),
        )
    )
    keyboard.add(
        get_back_inline_button_by_(
            callback_data=_get_new_callback_data(
                "get_posts", post_type, post_id
            )
        )
    )
    return keyboard


def get_confirmation_keyboard(
    post_id: str, post_type: str = "None"
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.insert(
        InlineKeyboardButton(
            text=_("Remove"),
            callback_data=_get_new_callback_data(
                "remove_post", post_type, post_id
            ),
        )
    )
    keyboard.insert(
        get_back_inline_button_by_(
            callback_data=_get_new_callback_data(
                "get_post", post_type, post_id
            )
        )
    )
    return keyboard
