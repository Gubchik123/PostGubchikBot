from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from loader import _


def get_post_creation_keyboard() -> ReplyKeyboardMarkup:
    """Returns reply keyboard for post content adding process."""
    return ReplyKeyboardMarkup(row_width=1, resize_keyboard=True).add(
        KeyboardButton(text=_("Next")),
        KeyboardButton(text=_("Cancel")),
    )
