from sqlalchemy.orm import Session
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


def _get_user_by_(session: Session, user_chat_id: int) -> User:
    """Returns user by the given session and user chat id."""
    return session.query(User).filter(User.chat_id == user_chat_id).first()


def get_user_by_(user_chat_id: int) -> User:
    """Returns user by the given user chat id."""
    with MySession() as session:
        return _get_user_by_(session, user_chat_id)


def get_user_channels_by_(user_chat_id: int) -> list[str]:
    """Returns user channels by the given user chat id."""
    with MySession() as session:
        return _get_user_by_(session, user_chat_id).channels.all()


def get_user_language_code_by_(user_chat_id: int) -> str | None:
    """Returns user language code by the given user chat id."""
    with MySession() as session:
        user = _get_user_by_(session, user_chat_id)
        return user.language_code if user else None


def change_user_language_by_(user_chat_id: int, language_code: str) -> None:
    """Changes user language by the given user chat id and language code."""
    with MySession() as session:
        user = _get_user_by_(session, user_chat_id)
        if user.language_code != language_code:
            user.language_code = language_code
            commit_and_refresh(session, user)


def change_user_timezone_by_(user_chat_id: int, timezone: str) -> None:
    """Changes user timezone by the given user chat id and timezone."""
    with MySession() as session:
        user = _get_user_by_(session, user_chat_id)
        if user.timezone != timezone:
            user.timezone = timezone
            commit_and_refresh(session, user)
