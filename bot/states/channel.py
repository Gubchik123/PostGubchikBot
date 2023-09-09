from aiogram.dispatcher.filters.state import State, StatesGroup


class Channel(StatesGroup):
    """States for channel creation."""

    forwarded_message = State()
