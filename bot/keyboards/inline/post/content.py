from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import _

from ..callback_data import (
    post_content_callback_data,
    get_back_inline_button_by_,
)


def _get_new_callback_data(level: str, content_index: int = 0) -> str:
    """Returns new post content callback data by the given parameters."""
    return post_content_callback_data.new(
        level=level, content_index=content_index
    )


def get_post_content_keyboard(content_item: dict) -> InlineKeyboardMarkup:
    """Returns inline keyboard with post content buttons by the given item."""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            text=_("Add URL buttons"),
            callback_data=_get_new_callback_data(
                "ask_for_url_buttons", content_item["index"]
            ),
        ),
    )
    if content_item["type"] == "message":
        mark = (
            "✅ "
            if content_item["kwargs"].get("disable_web_page_preview")
            else ""
        )
        keyboard.add(
            InlineKeyboardButton(
                text=mark + _("Disable web page preview"),
                callback_data=_get_new_callback_data(
                    "disable_web_page_preview", content_item["index"]
                ),
            ),
        )
    mark = "✅ " if content_item["kwargs"].get("disable_notification") else ""
    keyboard.add(
        InlineKeyboardButton(
            text=mark + _("Disable notification"),
            callback_data=_get_new_callback_data(
                "disable_notification", content_item["index"]
            ),
        ),
        InlineKeyboardButton(
            text=_("Remove content"),
            callback_data=_get_new_callback_data(
                "remove_content", content_item["index"]
            ),
        ),
    )
    return keyboard


def get_back_to_post_content_keyboard(
    content_index: int,
) -> InlineKeyboardMarkup:
    """Returns back keyboard for post content by the given index."""
    return InlineKeyboardMarkup().add(
        get_back_inline_button_by_(
            callback_data=_get_new_callback_data(
                "send_corrective_reply", content_index
            )
        )
    )


def get_url_buttons_keyboard_from_(
    user_message_text: str,
) -> InlineKeyboardMarkup:
    """
    Returns inline keyboard with url buttons from the given user message text.
    """
    keyboard = InlineKeyboardMarkup()
    for row in user_message_text.split("\n"):
        buttons = []
        for button in row.split("|"):
            text, url = button.split("-")
            buttons.append(
                InlineKeyboardButton(text=text.strip(), url=url.strip())
            )
        keyboard.row(*buttons)
    return keyboard
