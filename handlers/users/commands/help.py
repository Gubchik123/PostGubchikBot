from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp, _


@dp.message_handler(CommandHelp())
async def help_command(message: types.Message):
    """Handles /help command to show list of available commands."""
    await message.answer(
        _(
            "Available commands:\n"
            "/start - Start conversation\n"
            "/help - Get help\n"
            "/language - Change language"
        )
    )
