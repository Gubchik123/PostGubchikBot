from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import _
from data.config import CURRENCY_SYMBOL
from utils.db.models import Subscription
from .menu import get_back_to_menu_inline_button
from .callback_data import (
    subscription_callback_data,
    get_back_inline_button_by_,
)


def get_subscription_text_by_(subscription: Subscription) -> str:
    """Returns plan button text by the given subscription."""
    translated_plan_name = {
        "start": _("Start"),
        "pro": _("Pro"),
        "unlimited": _("Unlimited"),
    }.get(subscription.name)
    return f"{translated_plan_name} - {subscription.price} {CURRENCY_SYMBOL}"


def _get_new_callback_data(level: int, price="None") -> str:
    """Returns new subscription callback data by the given parameters."""
    return subscription_callback_data.new(level=level, price=price)


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            text=_("Update subscription"), callback_data="subscriptions"
        )
    )
    keyboard.add(get_back_to_menu_inline_button())
    return keyboard


def get_subscriptions_keyboard(
    all_subscriptions: list[Subscription],
) -> InlineKeyboardMarkup:
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


def get_invoice_keyboard(user_balance: int, price: int):
    CURRENT_LEVEL = 1

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            text=_("Pay for {price} {currency_symbol}").format(
                price=price, currency_symbol=CURRENCY_SYMBOL
            ),
            pay=True,
        )
    )
    if user_balance >= price:
        keyboard.add(
            InlineKeyboardButton(
                text=_("Charge from balance"),
                callback_data=_get_new_callback_data(CURRENT_LEVEL + 1, price),
            )
        )
    keyboard.add(
        get_back_inline_button_by_(callback_data="back_to_subscription")
    )
    return keyboard
