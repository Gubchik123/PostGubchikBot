from typing import Callable

from aiogram.types import CallbackQuery

from loader import dp, _
from utils.db.subscription_crud import get_all_subscriptions
from keyboards.inline.callback_data import subscription_callback_data
from keyboards.inline.subscription import (
    get_subscription_text_by_,
    get_subscriptions_keyboard,
    get_subscription_link_keyboard,
)


@dp.callback_query_handler(text="subscription")
async def get_subscriptions(query: CallbackQuery, *args) -> None:
    """Shows subscriptions to choose from."""
    all_subscriptions = get_all_subscriptions()
    subscriptions_text = ""
    for subscription in all_subscriptions:
        subscriptions_text += _(
            "{subscription_text}\n<i>Maximum channels: {max_channels}</i>\n\n"
        ).format(
            subscription_text=get_subscription_text_by_(subscription),
            max_channels=subscription.max_channels,
        )
    await query.message.edit_text(
        text=_(
            "☺️ <b>Subscription</b>\n\n"
            "You can add up to 3 channels to the bot <b>for free</b>.\n\n"
            "{subscriptions_text}"
            "<i>* All subscriptions for 30 days</i>"
        ).format(subscriptions_text=subscriptions_text),
        reply_markup=get_subscriptions_keyboard(all_subscriptions),
    )


async def get_subscription_link(query: CallbackQuery, price: int) -> None:
    """Shows subscription link."""
    await query.message.edit_text(
        text=_(
            "😋 To pay for a <b>30-day</b> subscription, follow the link below.\n\n"
            "<i>The subscription is activated automatically.</i>"
        ),
        reply_markup=get_subscription_link_keyboard(price),
    )


@dp.callback_query_handler(subscription_callback_data.filter())
async def navigate(query: CallbackQuery, callback_data: dict) -> None:
    """Catches all other subscription callback data to navigate."""
    current_level = callback_data.get("level")
    price = int(callback_data.get("price"))

    current_level_function: Callable = {
        "0": get_subscriptions,
        "1": get_subscription_link,
    }.get(current_level)

    await current_level_function(query, price)
