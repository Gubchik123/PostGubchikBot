from typing import Optional, Callable

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from loader import dp, _
from states.post import Post
from states.group import Group
from keyboards.default.post import get_post_creation_keyboard
from utils.db.crud.user import get_user_channels_by_, get_user_groups_by_
from utils.db.crud.group import create_group_by_, get_group_channel_titles_by_
from keyboards.inline.post.general import (
    get_channels_keyboard,
    get_post_album_keyboard,
)
from keyboards.inline.callback_data import (
    group_callback_data,
    get_keyboard_with_back_inline_button_by_,
)

from .album import post_album
from .constants import post_content, selected_channels


@dp.callback_query_handler(text="create_post", state="*")
async def get_channels(
    data: Message | CallbackQuery, state: Optional[FSMContext] = None
) -> None:
    """Sends a message with inline keyboard to select a channel."""
    if state:
        await state.finish()
    selected_channels.clear()
    answer_function: Callable = (
        data.message.edit_text
        if isinstance(data, CallbackQuery)
        else data.answer
    )
    await answer_function(
        text=_("Select the channel(s) you want to post to:"),
        reply_markup=get_channels_keyboard(
            get_user_channels_by_(data.from_user.id),
            get_user_groups_by_(data.from_user.id),
            selected_channels,
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
        reply_markup=get_channels_keyboard(
            user_channels,
            get_user_groups_by_(query.from_user.id),
            selected_channels,
        )
    )


@dp.callback_query_handler(group_callback_data.filter())
async def select_group_channels(
    query: CallbackQuery, callback_data: dict
) -> None:
    """Selects group channels by the group from the given callback data."""
    selected_channels.clear()
    selected_channels.extend(
        get_group_channel_titles_by_(callback_data["group_name"])
    )
    await query.answer()
    await ask_for_post_content(query)


async def ask_for_group_name(query: CallbackQuery, *args) -> None:
    """Asks for channel name and waits (state) for it."""
    await query.message.edit_text(
        text=_("Send me group name:"),
        reply_markup=get_keyboard_with_back_inline_button_by_("create_post"),
    )
    await Group.name.set()


@dp.message_handler(state=Group.name)
async def create_group(message: Message, state: FSMContext) -> None:
    """Creates a group by user input and selected channels."""
    await state.finish()
    create_group_by_(
        user_chat_id=message.from_user.id,
        group_name=message.text,
        group_target_menu="post creation",
        selected_channel_titles=selected_channels,
    )
    await get_channels(message)


async def ask_for_post_content(query: CallbackQuery, *args) -> None:
    """Asks for post content and waits (state) for it."""
    post_content.clear()
    await query.message.answer(
        text="🚀", reply_markup=get_post_creation_keyboard()
    )
    await query.message.edit_text(
        text=_(
            "You selected the {selected_channels} channel(s) to create a post\n\n"
            "Send me post content (text, photo, video, gif...)"
        ).format(selected_channels=", ".join(selected_channels)),
        reply_markup=get_post_album_keyboard(),
    )
    await Post.content.set()


async def ask_for_post_album(query: CallbackQuery, *args) -> None:
    """Asks for post album and waits (state) for it."""
    post_album.clear()
    await query.message.edit_text(
        text=_(
            "You selected the {selected_channels} channel(s) to create a post\n\n"
            "Send me post album (animation, document, audio, photo and video)\n\n"
            "<b>Important: album must contain content of the same type (e.g. only photos)</b>"
        ).format(selected_channels=", ".join(selected_channels))
    )
    await Post.album.set()
