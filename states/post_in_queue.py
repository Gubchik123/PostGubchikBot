from aiogram.dispatcher.filters.state import State, StatesGroup


class PostInQueue(StatesGroup):
    """States for post in queue creation."""

    date = State()
    time = State()
    interval = State()
