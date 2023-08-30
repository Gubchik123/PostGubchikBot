from aiogram import Dispatcher, executor

from loader import dp
from utils.db.db import Base, engine
import middlewares, filters, handlers
from utils.notify_admins import notify_admins
from utils.bot_commands import set_default_bot_commands


async def on_startup(dispatcher: Dispatcher) -> None:
    """Runs some functions on bot startup."""
    Base.metadata.create_all(bind=engine)
    await set_default_bot_commands(dispatcher)
    await notify_admins(dispatcher)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
