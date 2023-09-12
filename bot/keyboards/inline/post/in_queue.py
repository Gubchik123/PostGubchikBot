from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import _
from utils.post.settings import PostSettings
from keyboards.inline.callback_data import (
    posts_in_queue_callback_data,
    get_back_inline_button_by_,
)


def _get_new_callback_data(level: str, date: str = "None") -> str:
    """Returns new posts in queue callback data by the given parameters."""
    return posts_in_queue_callback_data.new(level=level, date=date)


def get_posts_in_queue_keyboard(
    post_settings: PostSettings,
) -> InlineKeyboardMarkup:
    """Returns inline keyboard
    with action buttons for posts in queue and back button."""
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text=("✅ " if post_settings.caption else "") + _("Add a caption"),
            callback_data=_get_new_callback_data("add_caption"),
        ),
        InlineKeyboardButton(
            text=("✅ " if post_settings.reply_markup else "")
            + _("Add URL buttons"),
            callback_data=_get_new_callback_data("add_url_buttons"),
        ),
        InlineKeyboardButton(
            text=("✅ " if post_settings.watermark else "")
            + _("Add watermark"),
            callback_data=_get_new_callback_data("add_watermark"),
        ),
        InlineKeyboardButton(
            text=("✅ " if post_settings.disable_web_page_preview else "")
            + _("Disable web page preview"),
            callback_data=_get_new_callback_data("disable_web_page_preview"),
        ),
        InlineKeyboardButton(
            text=("✅ " if post_settings.disable_notification else "")
            + _("Disable notification"),
            callback_data=_get_new_callback_data("disable_notification"),
        ),
        InlineKeyboardButton(
            text=("✅ " if post_settings.shuffle else "") + _("Shuffle posts"),
            callback_data=_get_new_callback_data("shuffle"),
        ),
        InlineKeyboardButton(
            text=_("Next"),
            callback_data=_get_new_callback_data("ask_for_start_date"),
        ),
    )


def get_date_keyboard() -> InlineKeyboardMarkup:
    """Returns inline keyboard with dates and back button."""
    keyboard = InlineKeyboardMarkup()
    keyboard.insert(
        InlineKeyboardButton(
            text=_("Today"),
            callback_data=_get_new_callback_data(
                "ask_for_time", date=datetime.today().strftime("%d.%m.%Y")
            ),
        )
    )
    keyboard.insert(
        InlineKeyboardButton(
            text=_("Tomorrow"),
            callback_data=_get_new_callback_data(
                "ask_for_time",
                date=(datetime.today() + timedelta(days=1)).strftime(
                    "%d.%m.%Y"
                ),
            ),
        )
    )
    keyboard.insert(
        InlineKeyboardButton(
            text=_("After tomorrow"),
            callback_data=_get_new_callback_data(
                "ask_for_time",
                date=(datetime.today() + timedelta(days=2)).strftime(
                    "%d.%m.%Y"
                ),
            ),
        )
    )
    keyboard.add(
        get_back_inline_button_by_(
            _get_new_callback_data("ask_for_what_to_add")
        )
    )
    return keyboard


def get_time_keyboard() -> InlineKeyboardMarkup:
    """Returns inline keyboard with time back button."""
    return InlineKeyboardMarkup().add(
        get_back_inline_button_by_(
            _get_new_callback_data("ask_for_start_date")
        )
    )


def get_interval_keyboard(date: str) -> InlineKeyboardMarkup:
    """Returns inline keyboard with interval back button."""
    return InlineKeyboardMarkup().add(
        get_back_inline_button_by_(
            _get_new_callback_data("ask_for_time", date)
        )
    )
