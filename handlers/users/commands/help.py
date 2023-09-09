from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp, _


@dp.message_handler(CommandHelp())
async def help_command(message: types.Message):
    """Handles /help command to show list of available commands."""
    await message.answer(
        _(
            "Available commands:\n"
            "/start - Start working with the bot\n"
            "/help - Send of basic usage rules\n"
            "/language - Change the language of the bot\n"
            "/menu - Send main menu\n"
        )
    )
