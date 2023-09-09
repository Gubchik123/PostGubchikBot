from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_language_inline_keyboard() -> InlineKeyboardMarkup:
    """Returns inline keyboard with language buttons."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Русский", callback_data="set_language_ru"
                ),
                InlineKeyboardButton(
                    text="English", callback_data="set_language_en"
                ),
            ],
        ],
    )
