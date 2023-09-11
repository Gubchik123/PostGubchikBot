from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from utils.db.db import engine, Base
from data.config import (
    BOT_TOKEN,
    I18N_DOMAIN,
    LOCALES_DIR,
    DEFAULT_TIMEZONE,
    SCHEDULER_JOBS_DATABASE_URL,
)
from middlewares import (
    ACLMiddleware,
    ThrottlingMiddleware,
)


storage = MemoryStorage()

bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

scheduler = AsyncIOScheduler(
    jobstores={
        "default": SQLAlchemyJobStore(
            url=SCHEDULER_JOBS_DATABASE_URL,
            engine=engine,
            tablename="apscheduler_jobs",
            metadata=Base.metadata,
        )
    },
    job_defaults={"misfire_grace_time": 15 * 60},  # 15 minutes
    timezone=DEFAULT_TIMEZONE,
)
scheduler.start()
scheduler.print_jobs()

i18n = ACLMiddleware(I18N_DOMAIN, LOCALES_DIR)
_ = i18n.gettext  # Alias for translation

dp.middleware.setup(ThrottlingMiddleware())
dp.middleware.setup(i18n)
