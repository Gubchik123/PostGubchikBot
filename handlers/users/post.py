from typing import Optional, Callable

from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from loader import dp, _
from states.post import Post
from .commands.menu import show_menu
from utils.post_content import PostContent
from utils.db.user_crud import get_user_channels_by_
from keyboards.inline.post import (
    get_channels_keyboard,
    get_pre_publish_keyboard,
)
from keyboards.inline.callback_data import (
    post_callback_data,
    get_keyboard_with_back_inline_button_by_,
)


selected_channels = []
post_content = PostContent()


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
    selected_channels.remove(
        channel_title
    ) if channel_title in selected_channels else selected_channels.append(
        channel_title
    )
    user_channels = get_user_channels_by_(query.from_user.id)
    if len(user_channels) == len(selected_channels):
        await ask_for_post_content(query)
        return
    await query.message.edit_reply_markup(
        reply_markup=get_channels_keyboard(user_channels, selected_channels)
    )


async def select_all_channels(query: CallbackQuery, **kwargs) -> None:
    """Selects all channels and updates the keyboard."""
    selected_channels.clear()
    for channel in get_user_channels_by_(query.from_user.id):
        selected_channels.append(channel.title)
    await ask_for_post_content(query)


async def ask_for_post_content(query: CallbackQuery, **kwargs) -> None:
    """Asks for post content and waits (state) for it."""
    post_content.clear()
    await query.message.edit_text(
        text=_(
            "You selected: {selected_channels}\n\n"
            "Send me post content (text, photo, video, gif...)\n\n"
            "To finish, send or click /stop\n"
            "To cancel, send or click /menu"
        ).format(selected_channels=", ".join(selected_channels)),
        reply_markup=get_keyboard_with_back_inline_button_by_(
            callback_data="create_post"
        ),
    )
    await Post.content.set()


@dp.message_handler(commands=["stop"], state=Post.content)
async def ask_about_time_to_publish_post(
    message: Message, state: FSMContext
) -> None:
    """Asks about time to publish the post."""
    await state.finish()
    await message.answer(
        text=_(
            "Post content is ready to publish into: {selected_channels}\n\n"
            "Do you want to publish it now or later?"
        ).format(selected_channels=", ".join(selected_channels)),
        reply_markup=get_pre_publish_keyboard(),
    )


async def publish_post(query: CallbackQuery, **kwargs) -> None:
    """Publishes the post into the selected channels."""
    await query.message.answer(_("Publishing..."))
    for channel in get_user_channels_by_(query.from_user.id):
        if channel.title in selected_channels:
            await post_content.send_to_(channel.chat_id)
    await query.message.answer(_("Published!"))
    post_content.clear()
    await show_menu(query)


@dp.callback_query_handler(post_callback_data.filter(), state="*")
async def navigate(query: CallbackQuery, callback_data: dict) -> None:
    """Catches all other post callback data to navigate."""
    current_level_function: Callable = {
        "select_or_remove_channel": select_or_remove_channel,
        "select_all_channels": select_all_channels,
        "ask_for_post_content": ask_for_post_content,
        "publish_post": publish_post,
        "postpone_post": None,
    }.get(callback_data.get("level"))

    await current_level_function(
        query, channel_title=callback_data.get("channel_title")
    )


# * Handlers for adding post content ------------------------------------------


@dp.message_handler(content_types=ContentType.TEXT, state=Post.content)
async def add_text_to_post(message: Message, state: FSMContext) -> None:
    """Adds text to the post content."""
    if message.text == "/menu":
        post_content.clear()
        await state.finish()
        await show_menu(message)
    post_content.add("message", message.text)


@dp.message_handler(content_types=ContentType.AUDIO, state=Post.content)
async def add_audio_to_post(message: Message, state: FSMContext) -> None:
    """Adds audio to the post content."""
    post_content.add("audio", message.audio.file_id)


@dp.message_handler(content_types=ContentType.DOCUMENT, state=Post.content)
async def add_document_to_post(message: Message, state: FSMContext) -> None:
    """Adds document to the post content."""
    post_content.add("document", message.document.file_id)


@dp.message_handler(content_types=ContentType.ANIMATION, state=Post.content)
async def add_animation_to_post(message: Message, state: FSMContext) -> None:
    """Adds animation to the post content."""
    post_content.add("animation", message.animation.file_id)


@dp.message_handler(content_types=ContentType.PHOTO, state=Post.content)
async def add_photo_to_post(message: Message, state: FSMContext) -> None:
    """Adds photo to the post content."""
    post_content.add("photo", message.photo[-1].file_id)


@dp.message_handler(content_types=ContentType.STICKER, state=Post.content)
async def add_sticker_to_post(message: Message, state: FSMContext) -> None:
    """Adds sticker to the post content."""
    post_content.add("sticker", message.sticker.file_id)


@dp.message_handler(content_types=ContentType.VIDEO, state=Post.content)
async def add_video_to_post(message: Message, state: FSMContext) -> None:
    """Adds video to the post content."""
    post_content.add("video", message.video.file_id)


@dp.message_handler(content_types=ContentType.VIDEO_NOTE, state=Post.content)
async def add_video_note_to_post(message: Message, state: FSMContext) -> None:
    """Adds video_note to the post content."""
    post_content.add("video_note", message.video_note.file_id)


@dp.message_handler(content_types=ContentType.VOICE, state=Post.content)
async def add_voice_to_post(message: Message, state: FSMContext) -> None:
    """Adds voice to the post content."""
    post_content.add("voice", message.voice.file_id)
