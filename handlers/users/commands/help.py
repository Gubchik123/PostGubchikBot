from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def help_command(message: types.Message):
    """Handles /help command to show list of available commands."""
    text = (
        "Commands list:",
        "/start - Start the bot",
        "/help - Get help",
    )
    await message.answer("\n".join(text))
