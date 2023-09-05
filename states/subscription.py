from aiogram.dispatcher.filters.state import State, StatesGroup


class Subscription(StatesGroup):
    """States for subscription editing."""

    price = State()
