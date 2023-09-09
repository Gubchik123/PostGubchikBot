from typing import Callable

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from loader import dp, _
from utils.db.crud.user import get_user_channels_by_
from keyboards.inline.post.general import get_pre_publish_keyboard

from ..commands.menu import show_menu
from .constants import post_content, selected_channels


@dp.callback_query_handler(text="time_to_publish_post", state="*")
async def ask_about_time_to_publish_post(
    data: Message | CallbackQuery, state: FSMContext
) -> None:
    """Asks about time to publish the post."""
    if state:
        await state.finish()
    answer_function: Callable = (
        data.message.edit_text
        if isinstance(data, CallbackQuery)
        else data.answer
    )
    await answer_function(
        text=_(
            "Post content is ready to publish into: {selected_channels}\n\n"
            "Do you want to publish it now or later?"
        ).format(selected_channels=", ".join(selected_channels)),
        reply_markup=get_pre_publish_keyboard(),
    )


async def publish_post(callback_query: CallbackQuery, *args) -> None:
    """Publishes the post into the selected channels."""
    await callback_query.message.answer(_("Publishing..."))
    for channel in get_user_channels_by_(callback_query.from_user.id):
        if channel.title in selected_channels:
            await post_content.send_to_(channel.chat_id)
    await callback_query.message.answer(_("Published!"))
    post_content.clear()
    # ! Workaround with user chat id to avoid "No channels" in the menu handler
    callback_query.message.from_user.id = callback_query.from_user.id
    await show_menu(callback_query.message)
