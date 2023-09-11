from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, _
from states.post import Post
from utils.post.album import PostAlbum

from ..commands.menu import show_menu
from .constants import post_content
from .publishing import ask_about_time_to_publish_post


global_post_album = PostAlbum()


@dp.message_handler(content_types=types.ContentType.TEXT, state=Post.album)
async def add_text_to_post(message: types.Message, state: FSMContext) -> None:
    """Handles action in text message from user."""
    if message.text == _("Cancel"):
        global_post_album.clear()
        await state.finish()
        await show_menu(message)
    elif message.text == _("Next"):
        post_content.add("album", global_post_album.get_album())
        await ask_about_time_to_publish_post(message, state)


@dp.message_handler(
    content_types=types.ContentType.ANIMATION, state=Post.album
)
async def handle_animation(message: types.Message):
    """Adds animation to the post album."""
    if (
        not global_post_album.media_type
        or global_post_album.media_type == "animation"
    ):
        global_post_album.add(
            types.InputMediaAnimation(media=message.animation.file_id)
        )
    else:
        await message.answer(_("You can't add animation into this album!"))


@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=Post.album)
async def handle_document(message: types.Message):
    """Adds document to the post album."""
    if (
        not global_post_album.media_type
        or global_post_album.media_type == "document"
    ):
        global_post_album.add(
            types.InputMediaDocument(media=message.document.file_id)
        )
    else:
        await message.answer(_("You can't add document into this album!"))


@dp.message_handler(content_types=types.ContentType.AUDIO, state=Post.album)
async def handle_audio(message: types.Message):
    """Adds audio to the post album."""
    if (
        not global_post_album.media_type
        or global_post_album.media_type == "audio"
    ):
        global_post_album.add(
            types.InputMediaAudio(media=message.audio.file_id)
        )
    else:
        await message.answer(_("You can't add audio into this album!"))


@dp.message_handler(content_types=types.ContentType.PHOTO, state=Post.album)
async def handle_photo(message: types.Message):
    """Adds photo to the post album."""
    if (
        not global_post_album.media_type
        or global_post_album.media_type == "photo"
    ):
        global_post_album.add(
            types.InputMediaPhoto(media=message.photo[-1].file_id)
        )
    else:
        await message.answer(_("You can't add photo into this album!"))


@dp.message_handler(content_types=types.ContentType.VIDEO, state=Post.album)
async def handle_video(message: types.Message):
    """Adds video to the post album."""
    if (
        not global_post_album.media_type
        or global_post_album.media_type == "video"
    ):
        global_post_album.add(
            types.InputMediaVideo(media=message.video.file_id)
        )
    else:
        await message.answer(_("You can't add video into this album!"))
