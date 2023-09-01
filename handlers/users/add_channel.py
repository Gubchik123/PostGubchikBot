from typing import Callable

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from loader import dp, _
from states.channel import Channel
from .commands.menu import show_menu
from keyboards.inline.menu import get_back_to_menu_inline_button
from utils.db.channel_crud import create_channel_by_


@dp.callback_query_handler(text="add_channel")
async def wait_for_forwarded_message(data: Message | CallbackQuery) -> None:
    """Asks for forwarded message to the channel and waits for it."""
    answer_function: Callable = (
        data.message.edit_text
        if isinstance(data, CallbackQuery)
        else data.answer
    )
    await answer_function(
        _(
            "Forward a message here from the channel you want to add.\n\n"
            "<b>Important:</b> the bot and you must be administrators"
            "in the channel from which you are forwarding the message."
        ),
        reply_markup=InlineKeyboardMarkup().add(
            get_back_to_menu_inline_button()
        ),
    )
    await Channel.forwarded_message.set()


@dp.message_handler(state=Channel.forwarded_message)
async def add_channel_by_forwarded_message(
    message: Message, state: FSMContext
) -> None:
    """Adds channel by forwarded message."""
    if message.text != "/menu":
        create_channel_by_(message.forward_from_chat, message.from_user.id)
    await state.finish()
    await show_menu(message)
