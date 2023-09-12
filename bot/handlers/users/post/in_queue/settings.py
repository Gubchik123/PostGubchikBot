import os
import platform
from io import BytesIO
from random import shuffle
from typing import Union, Callable

import requests
from PIL import Image, ImageDraw, ImageFont
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BadRequest
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
    content_types=ContentType.TEXT,
    state=PostContentSettings.watermark,
)
async def process_watermark_text(message: Message, state: FSMContext) -> None:
    """Processes watermark text."""
    await state.update_data(
        watermark_type="text",
        watermark_text=message.text,
        watermark_image_path=None,
    )
    await ask_for_watermark_size(
        message, message_text=_("Send me watermark font size (in px).")
    )


@dp.message_handler(
    content_types=ContentType.PHOTO,
    state=PostContentSettings.watermark,
)
async def process_watermark_image(message: Message, state: FSMContext) -> None:
    """Processes watermark image."""
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    await state.update_data(
        watermark_type="photo",
        watermark_image_path=file.file_path,
        watermark_text=None,
    )
    await ask_for_watermark_size(
        message,
        message_text=_(
            "Send me watermark size (in px) "
            "in the following format: widthxheight (for example: 100x100)."
        ),
    )


async def ask_for_watermark_size(message: Message, message_text: str) -> None:
    """Asks for watermark size to posts in queue and waits (state) for it."""
    await message.answer(
        message_text,
        reply_markup=get_keyboard_with_back_inline_button_by_(
            callback_data="posts_in_queue:ask_for_what_to_add:None"
        ),
    )
    await PostContentSettings.watermark_size.set()


@dp.message_handler(
    lambda message: message.text.isdigit(),
    content_types=ContentType.TEXT,
    state=PostContentSettings.watermark_size,
)
async def process_watermark_font_size(
    message: Message, state: FSMContext
) -> None:
    """Processes watermark font size."""
    watermark_size = int(message.text)
    if watermark_size < 1:
        await message.answer(_("Font size must be greater than 0!"))
        return
    await state.update_data(watermark_size=watermark_size)
    await ask_for_watermark_position(message)


@dp.message_handler(
    lambda message: "x" in message.text,
    content_types=ContentType.TEXT,
    state=PostContentSettings.watermark_size,
)
async def process_watermark_size(message: Message, state: FSMContext) -> None:
    """Processes watermark size."""
    watermark_size = message.text.split("x")
    try:
        watermark_size = tuple(map(int, watermark_size))
    except ValueError:
        await message.answer(
            _(
                "Watermark size must be in the following format: "
                "widthxheight (for example: 100x100)."
            )
        )
        return
    if watermark_size[0] < 1 or watermark_size[1] < 1:
        await message.answer(_("Watermark size must be greater than 0!"))
        return
    await state.update_data(watermark_size=watermark_size)
    await ask_for_watermark_position(message)


async def ask_for_watermark_position(message) -> None:
    """
    Asks for watermark position to posts in queue and waits (state) for it.
    """
    await message.answer(
        _("Send me watermark position (in px) in the following format: x,y."),
        reply_markup=get_keyboard_with_back_inline_button_by_(
            callback_data="posts_in_queue:ask_for_what_to_add:None"
        ),
    )
    await PostContentSettings.watermark_position.set()


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=PostContentSettings.watermark_position,
)
async def process_watermark_position(
    message: Message, state: FSMContext
) -> None:
    """Processes watermark position."""
    watermark_position = message.text.split(",")
    try:
        watermark_position = tuple(map(int, watermark_position))
    except ValueError:
        await message.answer(
            _(
                "Watermark position must be in the following format: x,y "
                "(for example: 100,100)."
            )
        )
        return
    if watermark_position[0] < 0 or watermark_position[1] < 0:
        await message.answer(_("Watermark position must be greater than 0!"))
        return
    await state.update_data(watermark_position=watermark_position)
    await ask_for_watermark_transparency(message)


async def ask_for_watermark_transparency(
    message: Message,
) -> None:
    """
    Asks for watermark transparency to posts in queue and waits (state) for it.
    """
    await message.answer(
        _("Send me watermark transparency (in %)."),
        reply_markup=get_keyboard_with_back_inline_button_by_(
            callback_data="posts_in_queue:ask_for_what_to_add:None"
        ),
    )
    await PostContentSettings.watermark_transparency.set()


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=PostContentSettings.watermark_transparency,
)
async def process_watermark_transparency(
    message: Message, state: FSMContext
) -> None:
    """Processes watermark transparency."""
    watermark_transparency = message.text
    if watermark_transparency.endswith("%"):
        watermark_transparency = watermark_transparency[:-1]
    try:
        watermark_transparency = int(watermark_transparency)
    except ValueError:
        await message.answer(
            _(
                "Watermark transparency must be in the following format: "
                "number% (for example: 50%)."
            )
        )
        return
    if watermark_transparency < 0 or watermark_transparency > 100:
        await message.answer(
            _("Watermark transparency must be between 0 and 100!")
        )
        return
    await state.update_data(watermark_transparency=watermark_transparency)
    await add_watermark_to_posts_in_queue(message, state)


async def add_watermark_to_posts_in_queue(
    message: Message, state: FSMContext
) -> None:
    """Adds watermark to images in the queue."""
    await message.answer(_("Processing..."))
    async with state.proxy() as state_data:
        await _add_watermark_to_posts_in_queue_by_(state_data)
    await state.finish()
    constants.post_content.settings.watermark = True
    await ask_for_what_to_add_to_posts_in_queue(message)


async def _add_watermark_to_posts_in_queue_by_(state_data: dict) -> None:
    """Adds watermark to images in the queue."""
    for image in constants.post_content.images:
        try:
            file = await bot.get_file(image["content"])
        except BadRequest:
            print(image["content"])
        output_image_path = _get_output_image_path(file.file_path, state_data)
        constants.post_content.update_by_(
            image["index"], f"Path:{output_image_path}"
        )


def _get_output_image_path(image_path: str, state_data: dict):
    """Returns output image path with watermark."""
    watermark_text = state_data.get("watermark_text")
    watermark_image_path = state_data.get("watermark_image_path")
    watermark_size = state_data.get("watermark_size")
    watermark_position = state_data.get("watermark_position")
    watermark_transparency = state_data.get("watermark_transparency")

    image = Image.open(_get_image_bytes_by_(image_path))
    watermarked_image = None

    if watermark_text:
        watermarked_image = Image.new("RGBA", image.size, (255, 255, 255, 0))
        watermarked_image.paste(image, (0, 0))
        draw = ImageDraw.Draw(watermarked_image)
        font = ImageFont.truetype(
            "arial.ttf" if platform.system() == "Windows" else "Ubuntu-M.ttf",
            size=watermark_size,
        )
        draw.text(
            watermark_position,
            watermark_text,
            fill=(255, 255, 255, watermark_transparency - 100),
            stroke_fill=(0, 0, 0, watermark_transparency - 100),
            font=font,
        )
    elif watermark_image_path:
        watermark = Image.open(
            _get_image_bytes_by_(watermark_image_path)
        ).convert("RGBA")
        watermark.thumbnail(watermark_size)
        transparent_watermark = Image.new("RGBA", image.size, (0, 0, 0, 0))
        watermark.putalpha(watermark_transparency + 100)
        transparent_watermark.paste(watermark, watermark_position, watermark)
        watermarked_image = Image.alpha_composite(
            image.convert("RGBA"), transparent_watermark
        )

    image_path = image_path.replace(".jpg", ".png")
    try:
        watermarked_image.save(image_path)
    except FileNotFoundError:
        os.makedirs("photos")
        watermarked_image.save(image_path)
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
