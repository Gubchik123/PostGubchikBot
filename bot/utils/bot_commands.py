from aiogram.types import BotCommand, BotCommandScopeDefault

from loader import bot


async def set_default_bot_commands(dp) -> None:
    """Sets default bot commands for en and ru languages."""
    bot_commands = {
        "en": [
            BotCommand("start", "Start working with the bot"),
            BotCommand("help", "Send of basic usage rules"),
            BotCommand("language", "Change the language of the bot"),
            BotCommand("menu", "Send main menu"),
        ],
        "ru": [
            BotCommand("start", "Начало работы з ботом"),
            BotCommand("help", "Отображение основных правил использования"),
            BotCommand("language", "Изменения языка бота"),
            BotCommand("menu", "Отправить главное меню"),
        ],
    }

    for language_code, commands in bot_commands.items():
        await bot.set_my_commands(
            commands=commands,
            scope=BotCommandScopeDefault(),
            language_code=language_code,
        )
