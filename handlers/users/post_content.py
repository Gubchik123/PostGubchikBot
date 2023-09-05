from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentType

from loader import dp
from .post import Post, post_content, show_menu


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
