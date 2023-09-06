from aiogram.dispatcher.filters.state import State, StatesGroup


class Post(StatesGroup):
    """States for post creation."""

    content = State()
    url_buttons = State()
    time = State()
    deletion_time = State()
