from typing import Optional

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from loader import dp, _
from states.post import Post
from utils.db.user_crud import get_user_channels_by_
from keyboards.default.post import get_post_creation_keyboard
from keyboards.inline.post.general import get_channels_keyboard

from .constants import post_content, selected_channels


@dp.callback_query_handler(text="create_post", state="*")
async def get_channels(
    query: CallbackQuery, state: Optional[FSMContext] = None
) -> None:
    """Sends a message with inline keyboard to select a channel."""
    if state:
        await state.finish()
    selected_channels.clear()
    await query.message.edit_text(
        text=_("Select the channel(s) you want to post to:"),
        reply_markup=get_channels_keyboard(
            get_user_channels_by_(query.from_user.id), selected_channels
        ),
    )


async def select_or_remove_channel(
    query: CallbackQuery, channel_title: str
) -> None:
    """Selects or removes the channel
    by the given channel title and updates the keyboard."""
    user_channels = get_user_channels_by_(query.from_user.id)
    if channel_title == "all":
        selected_channels.clear()
        selected_channels.extend([channel.title for channel in user_channels])
    else:
        selected_channels.remove(
            channel_title
        ) if channel_title in selected_channels else selected_channels.append(
            channel_title
        )
    await query.message.edit_reply_markup(
        reply_markup=get_channels_keyboard(user_channels, selected_channels)
    )


async def ask_for_post_content(query: CallbackQuery, *args) -> None:
    """Asks for post content and waits (state) for it."""
    post_content.clear()
    await query.message.edit_text(text="🚀")
    await query.message.answer(
        text=_(
            "You selected the {selected_channels} channel(s) to create a post\n\n"
            "Send me post content (text, photo, video, gif...)"
        ).format(selected_channels=", ".join(selected_channels)),
        reply_markup=get_post_creation_keyboard(),
    )
    await Post.content.set()
