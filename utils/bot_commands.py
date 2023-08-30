from aiogram import types


async def set_default_bot_commands(dp) -> None:
    """Sets default bot commands."""
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Start the bot"),
            types.BotCommand("help", "Get help"),
        ]
    )
