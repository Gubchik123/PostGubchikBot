from typing import Union, Callable

from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, Message, CallbackQuery

from loader import dp, _
from states.post import Post
from messages.post import get_asking_for_url_buttons_text
from keyboards.inline.callback_data import post_content_callback_data
from keyboards.inline.post.content import (
    get_url_buttons_keyboard_from_,
    get_post_content_keyboard,
    get_back_to_post_content_keyboard,
)

from . import constants
from ..commands.menu import show_menu
from .publishing import ask_about_time_to_publish_post
from .in_queue.settings.ask import ask_for_what_to_add_to_posts_in_queue


global_current_content_index = None


@dp.message_handler(content_types=ContentType.TEXT, state=Post.content)
async def add_text_to_post(message: Message, state: FSMContext) -> None:
    """Adds text to the post content."""
    if message.text == _("Cancel"):
        constants.post_content.clear()
        await state.finish()
        await show_menu(message)
    elif (
        message.text == _("Next")
        and constants.post_content.target_menu == "post creation"
    ):
        await ask_about_time_to_publish_post(message, state)
    elif (
        message.text == _("Next")
        and constants.post_content.target_menu == "post in queue"
    ):
        await state.finish()
        await ask_for_what_to_add_to_posts_in_queue(message)
    else:
        content_item = constants.post_content.add("message", message.text)
        await send_corrective_reply_to_(message, content_item)


@dp.message_handler(content_types=ContentType.AUDIO, state=Post.content)
async def add_audio_to_post(message: Message, state: FSMContext) -> None:
    """Adds audio to the post content."""
    content_item = constants.post_content.add("audio", message.audio.file_id)
    await send_corrective_reply_to_(message, content_item)


@dp.message_handler(content_types=ContentType.DOCUMENT, state=Post.content)
async def add_document_to_post(message: Message, state: FSMContext) -> None:
    """Adds document to the post content."""
    content_item = constants.post_content.add(
        "document", message.document.file_id
    )
    await send_corrective_reply_to_(message, content_item)


@dp.message_handler(content_types=ContentType.ANIMATION, state=Post.content)
async def add_animation_to_post(message: Message, state: FSMContext) -> None:
    """Adds animation to the post content."""
    content_item = constants.post_content.add(
        "animation", message.animation.file_id
    )
    await send_corrective_reply_to_(message, content_item)


@dp.message_handler(content_types=ContentType.PHOTO, state=Post.content)
async def add_photo_to_post(message: Message, state: FSMContext) -> None:
    """Adds photo to the post content."""
    content_item = constants.post_content.add(
        "photo", message.photo[-1].file_id
    )
    await send_corrective_reply_to_(message, content_item)


@dp.message_handler(content_types=ContentType.STICKER, state=Post.content)
async def add_sticker_to_post(message: Message, state: FSMContext) -> None:
    """Adds sticker to the post content."""
    content_item = constants.post_content.add(
        "sticker", message.sticker.file_id
    )
    await send_corrective_reply_to_(message, content_item)


@dp.message_handler(content_types=ContentType.VIDEO, state=Post.content)
async def add_video_to_post(message: Message, state: FSMContext) -> None:
    """Adds video to the post content."""
    content_item = constants.post_content.add("video", message.video.file_id)
    await send_corrective_reply_to_(message, content_item)


@dp.message_handler(content_types=ContentType.VIDEO_NOTE, state=Post.content)
async def add_video_note_to_post(message: Message, state: FSMContext) -> None:
    """Adds video_note to the post content."""
    content_item = constants.post_content.add(
        "video_note", message.video_note.file_id
    )
    await send_corrective_reply_to_(message, content_item)


@dp.message_handler(content_types=ContentType.VOICE, state=Post.content)
async def add_voice_to_post(message: Message, state: FSMContext) -> None:
    """Adds voice to the post content."""
    content_item = constants.post_content.add("voice", message.voice.file_id)
    await send_corrective_reply_to_(message, content_item)


async def send_corrective_reply_to_(
    data: Union[Message, CallbackQuery], content_item: Union[dict, int]
) -> None:
    """Sends corrective reply to the message."""
    content_item = (
        content_item
        if isinstance(content_item, dict)
        else constants.post_content.get_item_by_(
            content_item
        )  # content_item = content id
    )
    reply_function: Callable = (
        data.message.edit_text
        if isinstance(data, CallbackQuery)
        else data.reply
    )
    await reply_function(
        text=_("Content is added ✅"),
        reply_markup=get_post_content_keyboard(content_item),
    )


async def ask_for_url_buttons(
    callback_query: CallbackQuery, content_index: int
) -> None:
    """Asks for URL buttons and waits (state) for them."""
    global global_current_content_index
    global_current_content_index = content_index
    await callback_query.message.edit_text(
        text=get_asking_for_url_buttons_text(),
        reply_markup=get_back_to_post_content_keyboard(content_index),
    )
    await Post.url_buttons.set()


@dp.message_handler(state=Post.url_buttons)
async def add_url_buttons(message: Message, state: FSMContext):
    """Adds URL buttons to the post content."""
    constants.post_content.update_kwargs(
        global_current_content_index,
        "reply_markup",
        get_url_buttons_keyboard_from_(message.text),
    )
    await message.answer(
        text=_(
            "URL buttons are added ✅\n"
            "You can continue sending post content."
        )
    )
    await Post.content.set()


async def disable_web_page_preview(
    callback_query: CallbackQuery, content_index: int
) -> None:
    """Disables web page preview for the content with the given index."""
    content_item = constants.post_content.update_kwargs(
        content_index, "disable_web_page_preview"
    )
    await callback_query.message.edit_reply_markup(
        get_post_content_keyboard(content_item)
    )


async def disable_notification(
    callback_query: CallbackQuery, content_index: int
) -> None:
    """Disables notification for the content with the given index."""
    content_item = constants.post_content.update_kwargs(
        content_index, "disable_notification"
    )
    await callback_query.message.edit_reply_markup(
        get_post_content_keyboard(content_item)
    )


async def remove_content(
    callback_query: CallbackQuery, content_index: int
) -> None:
    """Removes the content with the given index."""
    constants.post_content.remove_by_(content_index)
    await callback_query.message.edit_text(_("Content is removed ❌"))


@dp.callback_query_handler(
    post_content_callback_data.filter(), state=(Post.content, Post.url_buttons)
)
async def navigate_all_other_post_content_callback_data(
    callback_query: CallbackQuery, callback_data: dict, state: FSMContext
) -> None:
    """Catches all other post callback data to navigate."""
    if (
        state
        and state.storage.data[str(state.user)][str(state.user)]["state"]
        == "Post:url_buttons"
    ):
        print("finish")
        await Post.content.set()
    current_level_function: Callable = {
        "send_corrective_reply": send_corrective_reply_to_,
        "ask_for_url_buttons": ask_for_url_buttons,
        "add_url_buttons": None,
        "disable_web_page_preview": disable_web_page_preview,
        "disable_notification": disable_notification,
        "remove_content": remove_content,
    }.get(callback_data.get("level"))

    await current_level_function(
        callback_query, int(callback_data.get("content_index"))
    )
