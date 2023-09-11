from aiogram.dispatcher.filters.state import State, StatesGroup


class PostContentSettings(StatesGroup):
    """States for post content settings."""

    caption = State()
    reply_markup = State()
    watermark = State()
