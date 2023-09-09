from aiogram.dispatcher.filters import Filter
from aiogram.types import Message, CallbackQuery

from data.config import ADMINS


class IsAdmin(Filter):
    """Filter for checking if user is admin."""

    async def check(self, data: Message | CallbackQuery) -> bool:
        """Returns True if user is admin and False otherwise."""
        return data.from_user.id in ADMINS
