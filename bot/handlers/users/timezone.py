from typing import Callable

from aiogram.types import CallbackQuery

from loader import dp, _
from .commands.menu import show_menu
from keyboards.inline.callback_data import timezone_callback_data
from utils.db.crud.user import get_user_by_, change_user_timezone_by_
from keyboards.inline.timezone import (
    get_countries_keyboard,
    get_cities_keyboard,
)


@dp.callback_query_handler(text="change_timezone")
async def get_countries(callback_query: CallbackQuery, *args) -> None:
    """Returns keyboard with countries to choose from."""
    user = get_user_by_(callback_query.from_user.id)
    await callback_query.message.edit_text(
        text=_(
            "<b>Changing timezone.</b>\n\n"
            "Your current timezone: <i>{timezone}</i>.\n"
            "You can choose a new time zone by choosing from the options below."
        ).format(timezone=user.timezone),
        reply_markup=get_countries_keyboard(),
    )


async def get_cities(
    callback_query: CallbackQuery, country: str, *args
) -> None:
    """Returns keyboard with cities to choose from."""
    await callback_query.message.edit_text(
        text=_("Choose a city in {country}:").format(country=country),
        reply_markup=get_cities_keyboard(country),
    )


async def change_timezone(
    callback_query: CallbackQuery, country: str, city: str
) -> None:
    """Changes user's timezone."""
    timezone = f"{country}/{city}"
    change_user_timezone_by_(callback_query.from_user.id, timezone)
    await callback_query.answer(
        text=_("Timezone successfully changed to {timezone}!").format(
            timezone=timezone
        )
    )
    await show_menu(callback_query)


@dp.callback_query_handler(timezone_callback_data.filter())
async def navigate_all_other_timezone_callback_data(
    callback_query: CallbackQuery, callback_data: dict
) -> None:
    """Catches all other timezone callback data to navigate."""

    current_level = callback_data.get("level")
    country = callback_data.get("country")
    city = callback_data.get("city")

    current_level_function: Callable = {
        "0": get_countries,
        "1": get_cities,
        "2": change_timezone,
    }.get(current_level)

    await current_level_function(callback_query, country, city)
