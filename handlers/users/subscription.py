from typing import Callable

from aiogram import types

from loader import bot, dp, _
from utils.db.models import User
from utils.db.crud.user import get_user_by_, change_user_balance
from keyboards.inline.callback_data import subscription_callback_data
from utils.db.subscription_crud import (
    get_all_subscriptions,
    add_subscription_for_user_with_,
)
from data.config import (
    CURRENCY,
    PAYMENTS_PROVIDER_TOKEN,
    PAYMENTS_IMAGE_URL,
    DEFAULT_MAX_FREE_CHANNELS,
    DEFAULT_SUBSCRIPTION_DAYS,
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
        data, user
    ) if user.subscription_id else await get_subscriptions(data)


async def get_user_subscription(
    data: types.Message | types.CallbackQuery, user: User
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
            subscription_text=get_subscription_text_by_(user.subscription),
            max_channels=user.subscription.max_channels,
            expire_date=user.subscription_expire_date.strftime(
                "%d.%m.%Y %H:%M"
            ),
        ),
        reply_markup=get_subscription_keyboard(),
    )


@dp.callback_query_handler(text="subscriptions")
async def get_subscriptions(
    data: types.Message | types.CallbackQuery, *args
) -> None:
    """Shows or sends subscriptions to choose from
    depending on the given data (message or callback)."""
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
            "You can add up to {DEFAULT_max_free_channels} channels to the bot <b>for free</b>.\n\n"
            "{subscriptions_text}"
            "<i>* All subscriptions for {default_subscription_days} days</i>"
        ).format(
            DEFAULT_max_free_channels=DEFAULT_MAX_FREE_CHANNELS,
            subscriptions_text=subscriptions_text,
            default_subscription_days=DEFAULT_SUBSCRIPTION_DAYS,
        ),
        reply_markup=get_subscriptions_keyboard(all_subscriptions),
    )


async def get_invoice(query: types.CallbackQuery, price: int) -> None:
    """Sends invoice."""
    if PAYMENTS_PROVIDER_TOKEN.split(":")[1] == "TEST":
        await query.answer(_("Test payment!"), show_alert=True)
    await bot.send_invoice(
        query.message.chat.id,
        title=_("Bot subscription"),
        description=_(
            "Bot subscription for {default_subscription_days} days"
        ).format(default_subscription_days=DEFAULT_SUBSCRIPTION_DAYS),
        provider_token=PAYMENTS_PROVIDER_TOKEN,
        currency=CURRENCY,
        photo_url=PAYMENTS_IMAGE_URL,
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[
            types.LabeledPrice(
                label=_(
                    "Subscription for {default_subscription_days} days"
                ).format(default_subscription_days=DEFAULT_SUBSCRIPTION_DAYS),
                amount=price * 100,
            )
        ],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload",
        reply_markup=get_invoice_keyboard(
            get_user_by_(query.from_user.id).balance, price
        ),
    )


async def charge_from_user_balance(
    query: types.CallbackQuery, price: int
) -> None:
    """Pays for subscription with user balance."""
    change_user_balance(query.from_user.id, -price)
    add_subscription_for_user_with_(query.from_user.id, price)
    await bot.send_message(
        query.message.chat.id,
        _(
            "We have successfully charged <b>{total_amount} {currency}</b> from your balance!\n\n"
            "<b>Subscription for {default_subscription_days} days is activated!</b>"
        ).format(
            total_amount=price,
            currency=CURRENCY,
            default_subscription_days=DEFAULT_SUBSCRIPTION_DAYS,
        ),
    )
    await back_to_subscription(query.message)


@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    """Answers pre checkout query (must be answered in 10 seconds)"""
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    """Handles successful payment."""
    await bot.send_message(message.chat.id, _("Processing..."))

    payment_info = message.successful_payment.to_python()
    price = payment_info["total_amount"] // 100

    add_subscription_for_user_with_(message.chat.id, price)
    await bot.send_message(
        message.chat.id,
        _(
            "Payment for <b>{total_amount} {currency}</b> is successful!\n\n"
            "<b>Subscription for {default_subscription_days} days is activated!</b>"
        ).format(
            total_amount=price,
            currency=payment_info["currency"],
            default_subscription_days=DEFAULT_SUBSCRIPTION_DAYS,
        ),
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
        "2": charge_from_user_balance,
    }.get(current_level)

    await current_level_function(query, price)
