from typing import Optional, Callable

from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext

from loader import dp
from keyboards.inline.callback_data import posts_in_queue_callback_data

from . import time, settings


@dp.callback_query_handler(posts_in_queue_callback_data.filter(), state="*")
async def navigate_all_other_posts_in_queue_callback_data(
    callback_query: CallbackQuery,
    callback_data: dict,
    state: Optional[FSMContext] = None,
) -> None:
    """Catches all other post callback data to navigate."""
    if state:
        await state.finish()
    current_level_function: Callable = {
        "ask_for_what_to_add": settings.ask.ask_for_what_to_add_to_posts_in_queue,
        # handlers to do something with posts in queue
        "add_caption": settings.caption.ask_for_caption_to_posts_in_queue,
        "add_url_buttons": settings.url_buttons.ask_for_url_buttons_to_posts_in_queue,
        "add_watermark": settings.watermark.ask_for_watermark_to_posts_in_queue,
        "disable_web_page_preview": settings.other.disable_web_page_preview_for_posts_in_queue,
        "disable_notification": settings.other.disable_notification_for_posts_in_queue,
        "shuffle": settings.other.shuffle_posts_in_queue,
        # handlers to set up posts in queue sending
        "ask_for_start_date": time.ask_for_start_date_to_send_posts_in_queue,
        "ask_for_time": time.ask_for_time_to_send_posts_in_queue,
        "ask_for_interval": time.ask_for_interval_to_send_posts_in_queue,
    }.get(callback_data.get("level"))

    try:
        await current_level_function(callback_query)
    except TypeError:
        await current_level_function(callback_query, callback_data.get("date"))
