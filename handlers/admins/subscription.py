from typing import Optional, Callable

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery

from loader import dp, _
from filters.admin import IsAdmin
from data.config import CURRENCY_SYMBOL
from states.subscription import Subscription
from keyboards.inline.callback_data import admin_subscription_callback_data
from keyboards.inline.admin_subscription import (
    get_subscriptions_keyboard,
    get_subscription_keyboard,
)
from utils.db.subscription_crud import (
    get_all_subscriptions,
    change_subscription_price_on_,
)

previous_price = None


@dp.message_handler(IsAdmin(), Command("subscription"))
@dp.callback_query_handler(IsAdmin(), text="admin_subscription", state="*")
async def show_subscriptions(
    data: Message | CallbackQuery, state: Optional[FSMContext] = None
) -> None:
    """Shows all subscriptions to choose from to change."""
    if state:
        await state.finish()
    answer_function: Callable = (
        data.message.edit_text
        if isinstance(data, CallbackQuery)
        else data.answer
    )
    await answer_function(
        _("Choose subscription to change:"),
        reply_markup=get_subscriptions_keyboard(get_all_subscriptions()),
    )


async def ask_for_new_price(query: CallbackQuery, price: int) -> None:
    """Asks admin for new subscription price."""
    global previous_price
    previous_price = price
    await query.message.edit_text(
        _(
            "Enter new subscription price"
            " (current price is {price} {currency_symbol})"
        ).format(price=price, currency_symbol=CURRENCY_SYMBOL),
        reply_markup=get_subscription_keyboard(),
    )
    await Subscription.price.set()


@dp.message_handler(
    lambda message: message.text.isdigit(), state=Subscription.price
)
async def change_subscription_price(
    message: Message, state: FSMContext
) -> None:
    """Changes subscription price."""
    new_price = int(message.text)
    change_subscription_price_on_(new_price, previous_price)
    await message.answer(
        _(
            "Subscription price has been changed"
            " from {previous_price} to {new_price}!"
        ).format(previous_price=previous_price, new_price=new_price),
    )
    await state.finish()
    await show_subscriptions(message)


@dp.callback_query_handler(admin_subscription_callback_data.filter())
async def navigate(query: CallbackQuery, callback_data: dict) -> None:
    """Catches all other admin subscription callback data to navigate."""
    current_level = callback_data.get("level")
    price = int(callback_data.get("price"))

    current_level_function: Callable = {
        "0": show_subscriptions,
        "1": ask_for_new_price,
    }.get(current_level)

    await current_level_function(query, price)
