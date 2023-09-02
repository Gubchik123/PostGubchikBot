from typing import Callable
from datetime import timedelta

from aiogram import types

from loader import bot, dp, _
from utils.db.models import Subscription
from utils.db.user_crud import get_user_by_
from data.config import PAYMENTS_PROVIDER_TOKEN, PAYMENTS_IMAGE_URL
from keyboards.inline.callback_data import subscription_callback_data
from utils.db.subscription_crud import (
    get_all_subscriptions,
    add_subscription_for_user_with_,
)
from keyboards.inline.subscription import (
    get_subscription_text_by_,
    get_subscription_keyboard,
    get_subscriptions_keyboard,
    get_invoice_keyboard,
)


@dp.callback_query_handler(text="back_to_subscription")
async def back_to_subscription(
    data: types.Message | types.CallbackQuery,
) -> None:
    """Workaround to get back to subscription menu
    depending on the given data (message or callback)."""
    if isinstance(data, types.CallbackQuery):
        await data.answer()
        await data.message.delete()  # because previous message is subscription menu
    else:
        await subscription(data)


@dp.callback_query_handler(text="subscription")
async def subscription(data: types.Message | types.CallbackQuery) -> None:
    """Shows or sends subscription details
    if user has subscription and shows or sends subscription menu otherwise."""
    user = get_user_by_(data.from_user.id)
    await get_user_subscription(
        data, user.subscription
    ) if user.subscription_id else await get_subscriptions(data)


async def get_user_subscription(
    data: types.Message | types.CallbackQuery, subscription: Subscription
) -> None:
    """Shows or sends user subscription info
    depending on the given data (message or callback)."""
    answer_function: Callable = (
        data.message.edit_text
        if isinstance(data, types.CallbackQuery)
        else data.answer
    )
    await answer_function(
        text=_(
            "☺️ <b>Subscription</b>\n\n"
            "You have <b>{subscription_text}</b> subscription.\n"
            "You can add up to <b>{max_channels}</b> channels.\n\n"
            "Your subscription will expire on <b>{expire_date}</b>."
        ).format(
            subscription_text=get_subscription_text_by_(subscription),
            max_channels=subscription.max_channels,
            expire_date=_get_expire_date_for_(subscription),
        ),
        reply_markup=get_subscription_keyboard(),
    )


def _get_expire_date_for_(subscription: Subscription) -> str:
    """Returns days left for the given subscription."""
    return str(
        (
            subscription.created + timedelta(days=subscription.duration_days)
        ).strftime("%d.%m.%Y %H:%M")
    )


async def get_subscriptions(
    data: types.Message | types.CallbackQuery, *args
) -> None:
    """Shows or sends subscriptions to choose from
    depending on the given data (message or callback)."""
    # TODO: Checking if user has subscription -> displaying info about it without payment buttons
    all_subscriptions = get_all_subscriptions()
    subscriptions_text = ""
    for subscription in all_subscriptions:
        subscriptions_text += _(
            "{subscription_text}\n<i>Maximum channels: {max_channels}</i>\n\n"
        ).format(
            subscription_text=get_subscription_text_by_(subscription),
            max_channels=subscription.max_channels,
        )
    answer_function: Callable = (
        data.message.edit_text
        if isinstance(data, types.CallbackQuery)
        else data.answer
    )
    await answer_function(
        text=_(
            "☺️ <b>Subscription</b>\n\n"
            "You can add up to 3 channels to the bot <b>for free</b>.\n\n"
            "{subscriptions_text}"
            "<i>* All subscriptions for 30 days</i>"
        ).format(subscriptions_text=subscriptions_text),
        reply_markup=get_subscriptions_keyboard(all_subscriptions),
    )


async def get_invoice(query: types.CallbackQuery, price: int) -> None:
    """Sends invoice."""
    if PAYMENTS_PROVIDER_TOKEN.split(":")[1] == "TEST":
        await query.answer(_("Test payment!"), show_alert=True)
    await bot.send_invoice(
        query.message.chat.id,
        title=_("Bot subscription"),
        description=_("Bot subscription for 30 days"),
        provider_token=PAYMENTS_PROVIDER_TOKEN,
        currency="UAH",
        photo_url=PAYMENTS_IMAGE_URL,
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[
            types.LabeledPrice(
                label=_("Subscription for 30 days"), amount=price * 100
            )
        ],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload",
        reply_markup=get_invoice_keyboard(price),
    )


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    """Answers pre checkout query (must be answered in 10 seconds)"""
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    """Handles successful payment."""
    payment_info = message.successful_payment.to_python()
    price = payment_info["total_amount"] // 100

    add_subscription_for_user_with_(message.chat.id, price)
    await bot.send_message(
        message.chat.id,
        _(
            "Payment for <b>{total_amount}</b> {currency} is successful!\n\n"
            "<b>Subscription for 30 days is activated!</b>"
        ).format(total_amount=price, currency=payment_info["currency"]),
    )
    await back_to_subscription(message)


@dp.callback_query_handler(subscription_callback_data.filter())
async def navigate(query: types.CallbackQuery, callback_data: dict) -> None:
    """Catches all other subscription callback data to navigate."""
    current_level = callback_data.get("level")
    price = int(callback_data.get("price"))

    current_level_function: Callable = {
        "0": get_subscriptions,
        "1": get_invoice,
    }.get(current_level)

    await current_level_function(query, price)
