from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp, _
from utils.db.user_crud import get_user_by_, create_user_by_
from .language import language_command


@dp.message_handler(CommandStart())
async def start_command(message: types.Message):
    """Handles /start command to create and greet user."""
    if get_user_by_(message.from_user.id) is None:
        create_user_by_(message.from_user, message.get_args())
    await language_command(message)
