from aiogram.dispatcher.filters.state import State, StatesGroup


class Group(StatesGroup):
    """States for Group creation."""

    name = State()
