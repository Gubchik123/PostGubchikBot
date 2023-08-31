from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.countries import COUNTRIES
from .menu import get_back_to_menu_inline_button
from .callback_data import timezone_callback_data


def _get_new_callback_data(
    level: int, country: str = "None", city: str = "None"
) -> str:
    """Returns new timezone callback data by the given parameters."""
    return timezone_callback_data.new(level=level, country=country, city=city)


def _get_back_inline_button_by_(current_level: int) -> InlineKeyboardButton:
    """Returns back button by the given current level."""
    return InlineKeyboardButton(
        text="🔙 Back",
        callback_data=_get_new_callback_data(current_level - 1),
    )


def get_countries_keyboard():
    CURRENT_LEVEL = 0

    keyboard = InlineKeyboardMarkup(row_width=3)

    for country in COUNTRIES:
        keyboard.insert(
            InlineKeyboardButton(
                text=country,
                callback_data=_get_new_callback_data(
                    CURRENT_LEVEL + 1, country
                ),
            )
        )
    keyboard.add(get_back_to_menu_inline_button())
    return keyboard


def get_cities_keyboard(country: str):
    CURRENT_LEVEL = 1

    keyboard = InlineKeyboardMarkup(row_width=5)

    for city in COUNTRIES[country]:
        keyboard.insert(
            InlineKeyboardButton(
                text=city,
                callback_data=_get_new_callback_data(
                    CURRENT_LEVEL + 1, country, city
                ),
            )
        )
    keyboard.add(_get_back_inline_button_by_(CURRENT_LEVEL))
    return keyboard
