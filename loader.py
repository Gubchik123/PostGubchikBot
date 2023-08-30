from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data.config import BOT_TOKEN, I18N_DOMAIN, LOCALES_DIR
from middlewares import ACLMiddleware, ThrottlingMiddleware


storage = MemoryStorage()

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
_ = i18n.gettext  # Alias for translation

dp.middleware.setup(ThrottlingMiddleware())
dp.middleware.setup(i18n)
