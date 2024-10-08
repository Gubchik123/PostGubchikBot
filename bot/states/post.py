from aiogram.dispatcher.filters.state import State, StatesGroup


class Post(StatesGroup):
    """States for post creation."""

    content = State()
    album = State()
    url_buttons = State()
    time = State()
    new_time = State()
    deletion_time = State()
