from aiogram import types

from loader import _
from .commands.menu import show_menu


async def greet_user(query: types.CallbackQuery):
    """Greets user after from /language command."""
    await query.answer(
        _("Hello, {name}!").format(name=query.from_user.full_name)
    )
    await show_menu(query)
