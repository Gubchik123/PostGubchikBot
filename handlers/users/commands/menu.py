from typing import Optional, Callable

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery

from loader import dp, _
from keyboards.inline.menu import get_menu_keyboard
from utils.db.crud.user import get_user_channels_by_


@dp.message_handler(Command("menu"))
@dp.callback_query_handler(text="menu", state="*")
async def show_menu(
    data: Message | CallbackQuery, state: Optional[FSMContext] = None
) -> None:
    """
    Shows or sends menu depending on the given data (message or callback).
    """
    if state:
        await state.finish()
    user_channels = get_user_channels_by_(data.from_user.id)
    has_channels = bool(user_channels)
    answer_function: Callable = (
        data.message.edit_text
        if isinstance(data, CallbackQuery)
        else data.answer
    )
    if has_channels:
        channel_list_items = "\n".join(
            [f"* {channel.title}" for channel in user_channels]
        )
        await answer_function(
            text=_(
                "Your channels:\n{channel_list_items}\n\n"
                "Choose one of the buttons below:"
            ).format(channel_list_items=channel_list_items),
            reply_markup=get_menu_keyboard(has_channels=True),
        )
    else:
        await answer_function(
            text=_(
                "You currently have no channels.\n\n"
                "Choose one of the buttons below:"
            ),
            reply_markup=get_menu_keyboard(has_channels=False),
        )
