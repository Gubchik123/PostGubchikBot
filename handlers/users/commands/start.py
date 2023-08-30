from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from utils.db.models import User
from utils.db.db import add_commit_and_refresh


@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    """Handles /start command to create and greet user."""
    add_commit_and_refresh(
        User(
            chat_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
    )
    await message.answer(f"Hello, {message.from_user.full_name}!")
