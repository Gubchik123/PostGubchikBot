from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp
from utils.db.user_crud import change_user_language_by_
from handlers.users.callback_handlers import greet_user
from keyboards.inline.language import get_language_inline_keyboard


@dp.message_handler(Command("language"))
async def language_command(message: types.Message):
    """Handles /language command to change user's language."""
    await message.answer(
        "Выбирите язык | Choose language",
        reply_markup=get_language_inline_keyboard(),
    )


@dp.callback_query_handler(text_contains="set_language_ru")
async def set_language_ru_callback_handler(query: types.CallbackQuery):
    """Handles setting Russian language callback."""
    change_user_language_by_(query.from_user.id, "ru")
    await query.answer("Язык изменен на русский")
    await greet_user(query)


@dp.callback_query_handler(text_contains="set_language_en")
async def set_language_en_callback_handler(query: types.CallbackQuery):
    """Handles setting English language callback."""
    change_user_language_by_(query.from_user.id, "en")
    await query.answer("Language changed to English")
    await greet_user(query)
