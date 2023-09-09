from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import _
from keyboards.inline.callback_data import (
    posts_in_queue_callback_data,
    get_back_inline_button_by_,
)


def _get_new_callback_data(
    level: str, date: str = "None"
) -> str:
    """Returns new posts in queue callback data by the given parameters."""
    return posts_in_queue_callback_data.new(
        level=level, date=date
    )


def get_posts_in_queue_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(
            text=_("Add a signature"),
            callback_data=_get_new_callback_data("add_signature"),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Add URL buttons"),
            callback_data=_get_new_callback_data("add_url_buttons"),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Add watermark"),
            callback_data=_get_new_callback_data("add_watermark"),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Remove author text"),
            callback_data=_get_new_callback_data("remove_author_text"),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Disable web page preview"),
            callback_data=_get_new_callback_data("disable_web_page_preview"),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Disable notification"),
            callback_data=_get_new_callback_data("disable_notification"),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Send as album"),
            callback_data=_get_new_callback_data(
                "send_posts_in_queue_as_album"
            ),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Shuffle posts"),
            callback_data=_get_new_callback_data("shuffle"),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text=_("Next"),
            callback_data=_get_new_callback_data("ask_for_start_date"),
        )
    )
    return keyboard


def get_date_keyboard() -> InlineKeyboardMarkup:
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
    return InlineKeyboardMarkup().add(
        get_back_inline_button_by_(
            _get_new_callback_data("ask_for_start_date")
        )
    )


def get_interval_keyboard(date: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup().add(
        get_back_inline_button_by_(
            _get_new_callback_data("ask_for_time", date)
        )
    )
