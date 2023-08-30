from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from utils.db.user_crud import create_user_by_


@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    """Handles /start command to create and greet user."""
    create_user_by_(message.from_user)
    await message.answer(f"Hello, {message.from_user.full_name}!")
