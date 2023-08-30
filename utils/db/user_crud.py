from aiogram.types import User as TelegramUser

from .models import User
from .db import MySession, commit_and_refresh, add_commit_and_refresh


def create_user_by_(telegram_user: TelegramUser) -> None:
    """Creates user in database by the given telegram user."""
    add_commit_and_refresh(
        User(
            chat_id=telegram_user.id,
            username=telegram_user.username,
            full_name=telegram_user.full_name,
        )
    )
