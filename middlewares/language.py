from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware

from utils.db.user_crud import get_user_language_code_by_


class ACLMiddleware(I18nMiddleware):
    """Middleware for getting user language."""

    async def get_user_locale(self, action, args):
        """Returns user language code from db or from telegram profile."""
        telegram_user = types.User.get_current()
        return (
            get_user_language_code_by_(telegram_user.id)
            or telegram_user.locale
        )
