from typing import NoReturn

from aiogram import types, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


class ThrottlingMiddleware(BaseMiddleware):
    """Simple middleware"""

    def __init__(
        self, limit: float = DEFAULT_RATE_LIMIT, key_prefix: str = "antiflood_"
    ) -> None:
        """Initialize middleware."""
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(
        self, message: types.Message, data: dict
    ) -> None | NoReturn:
        """Process message."""
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            limit = getattr(handler, "throttling_rate_limit", self.rate_limit)
            key = getattr(
                handler, "throttling_key", f"{self.prefix}_{handler.__name__}"
            )
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self.message_throttled(message, t)
            raise CancelHandler()

    async def message_throttled(
        self, message: types.Message, throttled: Throttled
    ) -> None:
        """Notify user about throttling."""
        if throttled.exceeded_count <= 2:
            await message.reply("Too many requests!")
