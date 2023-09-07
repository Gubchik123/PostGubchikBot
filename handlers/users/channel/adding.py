from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from loader import dp, _
from states.channel import Channel
from data.config import DEFAULT_MAX_FREE_CHANNELS
from utils.db.channel_crud import create_channel_by_
from keyboards.inline.menu import get_back_to_menu_keyboard
from utils.db.user_crud import get_user_by_, get_user_channels_by_

from ..commands.menu import show_menu


@dp.callback_query_handler(text="add_channel")
async def check_if_user_can_add_channel(query: CallbackQuery) -> None:
    """Checks if user can add channel
    and shows the next instructions if True and message otherwise."""
    if not _can_user_add_channel(query.from_user.id):
        await query.message.edit_text(
            _("You have reached the limit of channels!"),
            reply_markup=get_back_to_menu_keyboard(),
        )
        return
    await ask_for_forwarded_message(query)


def _can_user_add_channel(user_chat_id: int) -> bool:
    """Returns True if user can add channel and False otherwise."""
    user = get_user_by_(user_chat_id)
    user_channels_count = len(get_user_channels_by_(user_chat_id))
    if (
        not user.subscription_id
        and user_channels_count + 1 > DEFAULT_MAX_FREE_CHANNELS
    ):
        return False
    elif (
        user.subscription_id
        and user_channels_count + 1 > user.subscription.max_channels
    ):
        return False
    return True


async def ask_for_forwarded_message(query: CallbackQuery) -> None:
    """Asks for forwarded message to the channel and waits (state) for it."""
    await query.message.edit_text(
        _(
            "Forward a message here from the channel you want to add.\n\n"
            "<b>Important:</b> the bot and you must be administrators"
            "in the channel from which you are forwarding the message."
        ),
        reply_markup=get_back_to_menu_keyboard(),
    )
    await Channel.forwarded_message.set()


@dp.message_handler(
    lambda message: message.forward_from_chat, state=Channel.forwarded_message
)
async def add_channel_by_forwarded_message(
    message: Message, state: FSMContext
) -> None:
    """Adds channel by forwarded message."""
    if message.text != "/menu":
        create_channel_by_(message.forward_from_chat, message.from_user.id)
    await state.finish()
    await show_menu(message)
