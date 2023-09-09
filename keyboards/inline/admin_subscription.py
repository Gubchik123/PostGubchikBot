from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.db.models import Subscription
from .menu import get_back_to_menu_inline_button
from .subscription import get_subscription_text_by_
from .callback_data import admin_subscription_callback_data


def _get_new_callback_data(level: int, price="None") -> str:
    """Returns new admin subscription callback data by the given parameters."""
    return admin_subscription_callback_data.new(level=level, price=price)


def get_subscriptions_keyboard(
    all_subscriptions: list[Subscription],
) -> InlineKeyboardMarkup:
    """Returns inline keyboard with subscriptions and back button."""
    CURRENT_LEVEL = 0

    keyboard = InlineKeyboardMarkup(row_width=1)

    for subscription in all_subscriptions:
        keyboard.add(
            InlineKeyboardButton(
                text=get_subscription_text_by_(subscription),
                callback_data=_get_new_callback_data(
                    CURRENT_LEVEL + 1, subscription.price
                ),
            )
        )
    keyboard.add(get_back_to_menu_inline_button())
    return keyboard
