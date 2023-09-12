import os
from io import BytesIO
from random import shuffle
from typing import Union, Callable, Optional, Tuple

import requests
from PIL import Image, ImageDraw, ImageFont
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, Message, CallbackQuery

from loader import bot, dp, _
from data.config import BOT_TOKEN
from utils.post.settings import PostSettings
from states.post_settings import PostContentSettings
from messages.post import get_asking_for_url_buttons_text
from keyboards.inline.post.in_queue import get_posts_in_queue_keyboard
from keyboards.inline.post.content import get_url_buttons_keyboard_from_
from keyboards.inline.callback_data import (
    get_keyboard_with_back_inline_button_by_,
)

from .. import constants
from ..channels import get_channels


@dp.callback_query_handler(text="posts_in_queue")
async def get_channels_(callback_query: CallbackQuery) -> None:
    """Sends a message with inline keyboard to select a channel."""
    constants.post_content.settings = PostSettings()
    await get_channels(callback_query, target="post in queue")


async def ask_for_what_to_add_to_posts_in_queue(
    data: Union[Message, CallbackQuery],
) -> None:
    """Asks for what to add to posts in queue."""
    answer_function: Callable = (
        data.message.edit_text
        if isinstance(data, CallbackQuery)
        else data.answer
    )
    await answer_function(
        _("Select what you want to add to all posts in the queue:"),
        reply_markup=get_posts_in_queue_keyboard(
            constants.post_content.settings
        ),
    )


async def ask_for_caption_to_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Asks for caption to posts in queue and waits (state) for it."""
    await callback_query.message.edit_text(
        text=_("Send me new caption for all posts in the queue."),
        reply_markup=get_keyboard_with_back_inline_button_by_(
            callback_data="posts_in_queue:ask_for_what_to_add:None"
        ),
    )
    await PostContentSettings.caption.set()


@dp.message_handler(state=PostContentSettings.caption)
async def add_caption_to_posts_in_queue(message: Message) -> None:
    """Adds caption to posts in queue."""
    constants.post_content.settings.caption = message.text
    await ask_for_what_to_add_to_posts_in_queue(message)


async def ask_for_url_buttons_to_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Adds url buttons to posts in queue."""
    await callback_query.message.edit_text(
        text=get_asking_for_url_buttons_text(),
        reply_markup=get_keyboard_with_back_inline_button_by_(
            callback_data="posts_in_queue:ask_for_what_to_add:None"
        ),
    )
    await PostContentSettings.reply_markup.set()


@dp.message_handler(state=PostContentSettings.reply_markup)
async def add_url_buttons_to_posts_in_queue(message: Message) -> None:
    """Adds url buttons to posts in queue."""
    constants.post_content.settings.reply_markup = (
        get_url_buttons_keyboard_from_(message.text)
    )
    await ask_for_what_to_add_to_posts_in_queue(message)


async def _can_add_watermark(callback_query: CallbackQuery) -> bool:
    """Checks if watermark can be added to posts in queue."""
    if constants.post_content.settings.watermark is True:
        callback_query.answer()
        return False
    if constants.post_content.settings.watermark is False:
        await callback_query.answer(
            _("You can't add watermark to posts in queue!"), show_alert=True
        )
        return False
    if not constants.post_content.is_there_images:
        constants.post_content.settings.watermark = False
        await callback_query.answer(
            _("There are no images in the queue."), show_alert=True
        )
        return False
    return True


async def ask_for_watermark_to_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Asks for watermark to posts in queue and waits (state) for it."""
    if not await _can_add_watermark(callback_query):
        return
    await callback_query.answer(
        _("Pay attention that you can't edit watermark for posts in queue!"),
        show_alert=True,
    )
    await callback_query.message.edit_text(
        text=_(
            "Send me new watermark (image or text) for all images in the queue."
        ),
        reply_markup=get_keyboard_with_back_inline_button_by_(
            callback_data="posts_in_queue:ask_for_what_to_add:None"
        ),
    )
    await PostContentSettings.watermark.set()


@dp.message_handler(
    content_types=[ContentType.TEXT, ContentType.PHOTO],
    state=PostContentSettings.watermark,
)
async def add_watermark_image_to_posts_in_queue(
    message: Message, state: FSMContext
) -> None:
    """Adds watermark to images in the queue."""
    await message.answer(_("Processing..."))
    await _add_watermark_to_posts_in_queue_by_(message)
    await state.finish()
    constants.post_content.settings.watermark = True
    await ask_for_what_to_add_to_posts_in_queue(message)


async def _add_watermark_to_posts_in_queue_by_(message: Message) -> None:
    """Adds watermark to images in the queue."""
    (
        watermark_text,
        watermark_image_path,
    ) = await _get_watermark_text_and_image_path_by_(message)

    for image in constants.post_content.images:
        file = await bot.get_file(image["content"])
        output_image_path = _get_output_image_path(
            file.file_path, watermark_text, watermark_image_path
        )
        constants.post_content.update_by_(
            image["index"], f"Path:{output_image_path}"
        )


async def _get_watermark_text_and_image_path_by_(
    message: Message,
) -> Tuple[Union[str, None], Union[str, None]]:
    """Returns watermark text and image path by the given message."""
    if message.content_type == ContentType.TEXT:
        watermark_text = message.text
        watermark_image_path = None
    elif message.content_type == ContentType.PHOTO:
        photo = message.photo[-1]
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        watermark_image_path = file.file_path
        watermark_text = None
    return watermark_text, watermark_image_path


def _get_output_image_path(
    image_path: str,
    watermark_text: Optional[str] = None,
    watermark_image_path: Optional[str] = None,
):
    """Returns output image path with watermark."""
    image = Image.open(_get_image_bytes_by_(image_path))
    width, height = image.size

    if watermark_text:
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", size=36)
        text_length = draw.textlength(watermark_text, font)
        x = width - text_length - 10
        y = height - 50
        draw.text((x, y), watermark_text, fill="white", font=font)
    elif watermark_image_path:
        watermark = Image.open(_get_image_bytes_by_(watermark_image_path))
        watermark.thumbnail((100, 100))
        image.paste(watermark, (width - 100 - 10, height - 100 - 15))

    try:
        image.save(image_path)
    except FileNotFoundError:
        os.makedirs("photos")
        image.save(image_path)
    return image_path


def _get_image_bytes_by_(image_path: str) -> BytesIO:
    """Returns image bytes by the given image path."""
    response = requests.get(
        f"https://api.telegram.org/file/bot{BOT_TOKEN}/{image_path}"
    )
    return BytesIO(response.content)


async def disable_web_page_preview_for_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Disables web page preview for posts in queue."""
    constants.post_content.settings.disable_web_page_preview = (
        not constants.post_content.settings.disable_web_page_preview
    )
    await callback_query.message.edit_reply_markup(
        reply_markup=get_posts_in_queue_keyboard(
            constants.post_content.settings
        )
    )


async def disable_notification_for_posts_in_queue(
    callback_query: CallbackQuery,
) -> None:
    """Disables notification for posts in queue."""
    constants.post_content.settings.disable_notification = (
        not constants.post_content.settings.disable_notification
    )
    await callback_query.message.edit_reply_markup(
        reply_markup=get_posts_in_queue_keyboard(
            constants.post_content.settings
        )
    )


async def shuffle_posts_in_queue(callback_query: CallbackQuery) -> None:
    """Shuffles posts in queue."""
    if not constants.post_content.settings.shuffle:
        shuffle(constants.post_content.content)
        constants.post_content.settings.shuffle = True
        await callback_query.message.edit_reply_markup(
            reply_markup=get_posts_in_queue_keyboard(
                constants.post_content.settings
            )
        )
    else:
        await callback_query.answer(_("Posts are already shuffled."))
