from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp


@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    """Handles /start command to greet user."""
    await message.answer(f"Hello, {message.from_user.full_name}!")
