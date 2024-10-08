from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp, _
from .menu import show_menu
from utils.db.crud.user import change_user_language_by_
from keyboards.inline.language import get_language_inline_keyboard


@dp.message_handler(Command("language"))
async def language_command(message: types.Message):
    """Handles /language command to change user's language."""
    await message.answer(
        "Выбирите язык | Choose language",
        reply_markup=get_language_inline_keyboard(),
    )


@dp.callback_query_handler(text_contains="set_language_ru")
async def set_language_ru_callback_handler(
    callback_query: types.CallbackQuery,
):
    """Handles setting Russian language callback."""
    change_user_language_by_(callback_query.from_user.id, "ru")
    await callback_query.answer("Язык изменен на русский")
    await greet_user(callback_query)


@dp.callback_query_handler(text_contains="set_language_en")
async def set_language_en_callback_handler(
    callback_query: types.CallbackQuery,
):
    """Handles setting English language callback."""
    change_user_language_by_(callback_query.from_user.id, "en")
    await callback_query.answer("Language changed to English")
    await greet_user(callback_query)


async def greet_user(callback_query: types.CallbackQuery):
    """Greets user after from /language command."""
    await callback_query.answer(
        _("Hello, {name}!").format(name=callback_query.from_user.full_name)
    )
    await show_menu(callback_query)
