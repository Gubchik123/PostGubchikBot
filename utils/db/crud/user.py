from sqlalchemy import update
from sqlalchemy.orm import Session
from aiogram.types import User as TelegramUser

from data.config import DEFAULT_REFERRAL_BONUS

from ..models import User, Channel, Group
from ..db import MySession, commit_and_refresh, add_commit_and_refresh


users = {}
channels = {}
groups = {}


def _get_user_by_(session: Session, user_chat_id: int) -> User:
    """Returns user by the given session and user chat id."""
    return session.query(User).filter(User.chat_id == user_chat_id).first()


def _is_valid_referral_(message_args: str, invited_user_chat_id: int) -> bool:
    """Checks if referral is valid
    by the given message args and invited user chat id."""
    if len(message_args) not in (9, 10) and not message_args.isdigit():
        return False
    user_who_invite_chat_id = int(message_args)
    if user_who_invite_chat_id == invited_user_chat_id:
        return False
    return True


def _add_referral_by_(user_who_invite_chat_id: int) -> None:
    """Adds referral by the given invited user chat id and message args."""
    with MySession() as session:
        user_who_invite = _get_user_by_(session, user_who_invite_chat_id)
        if user_who_invite:
            user_who_invite.referrals += 1
            user_who_invite.balance += DEFAULT_REFERRAL_BONUS
            commit_and_refresh(session, user_who_invite)


def create_user_by_(telegram_user: TelegramUser, message_args: str) -> None:
    """Creates user in database by the given telegram user."""
    if _is_valid_referral_(message_args, telegram_user.id):
        _add_referral_by_(int(message_args))
    add_commit_and_refresh(
        User(
            chat_id=telegram_user.id,
            username=telegram_user.username,
            full_name=telegram_user.full_name,
        )
    )


def get_user_by_(user_chat_id: int) -> User:
    """Returns user by the given user chat id."""
    try:
        return users[user_chat_id]
    except KeyError:
        with MySession() as session:
            user = _get_user_by_(session, user_chat_id)
        users[user_chat_id] = user
        return user


def get_user_channels_by_(user_chat_id: int) -> list[Channel]:
    """Returns user channels by the given user chat id."""
    try:
        return channels[user_chat_id]
    except KeyError:
        with MySession() as session:
            user_channels = _get_user_by_(session, user_chat_id).channels.all()
        channels[user_chat_id] = user_channels
        return user_channels


def get_user_groups_by_(user_chat_id: int) -> list[Group]:
    """Returns user groups by the given user chat id."""
    try:
        return groups[user_chat_id]
    except KeyError:
        with MySession() as session:
            user_groups = _get_user_by_(session, user_chat_id).groups.all()
        groups[user_chat_id] = user_groups
        return user_groups


def get_user_language_code_by_(user_chat_id: int) -> str | None:
    """Returns user language code by the given user chat id."""
    user = get_user_by_(user_chat_id)
    return user.language_code if user else None


def change_user_language_by_(user_chat_id: int, language_code: str) -> None:
    """Changes user language by the given user chat id and language code."""
    with MySession() as session:
        session.execute(
            update(User)
            .where(User.chat_id == user_chat_id)
            .values(language_code=language_code)
        )
        session.commit()
    if users[user_chat_id]:
        users[user_chat_id].language_code = language_code


def change_user_timezone_by_(user_chat_id: int, timezone: str) -> None:
    """Changes user timezone by the given user chat id and timezone."""
    with MySession() as session:
        session.execute(
            update(User)
            .where(User.chat_id == user_chat_id)
            .values(timezone=timezone)
        )
        session.commit()
    users[user_chat_id].timezone = timezone


def reset_user_subscription_by_(user_chat_id: int) -> None:
    """Resets user subscription by the given user chat id."""
    with MySession() as session:
        session.execute(
            update(User)
            .where(User.chat_id == user_chat_id)
            .values(subscription_id=None, subscription_expire_date=None)
        )
        session.commit()
    users[user_chat_id].subscription = None
    users[user_chat_id].subscription_expire_date = None


def change_user_balance(user_chat_id: int, charge_price: int) -> None:
    """Changes user balance by the given user chat id and charge price."""
    with MySession() as session:
        session.execute(
            update(User)
            .where(User.chat_id == user_chat_id)
            .values(balance=User.balance + charge_price)
        )
        session.commit()
    users[user_chat_id].balance += charge_price
