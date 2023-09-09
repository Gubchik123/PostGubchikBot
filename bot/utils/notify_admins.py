import logging

from aiogram import Dispatcher

from data.config import ADMINS


async def notify_admins(dp: Dispatcher) -> None:
    """Notifies admins on bot startup."""
    for admin in ADMINS:
        try:
            await dp.bot.send_message(admin, "Bot started!")
        except Exception as err:
            logging.exception(err)
