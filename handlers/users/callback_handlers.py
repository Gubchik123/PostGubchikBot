from aiogram import types

from loader import _


async def greet_user(query: types.CallbackQuery):
    """Greets user after from /language command."""
    await query.message.edit_text(
        _("Hello, {name}!").format(name=query.from_user.full_name)
    )
