from aiogram.types import Chat

from .user import channels
from ..models import Channel
from ..db import MySession, add_commit_and_refresh


def create_channel_by_(chat: Chat, user_chat_id: int) -> None:
    """Creates channel by the given telegram chat for the given user."""
    add_commit_and_refresh(
        Channel(
            chat_id=chat.id,
            title=chat.title,
            username=chat.username,
            bio=chat.bio,
            description=chat.description,
            user_id=user_chat_id,
        )
    )
    channels.pop(user_chat_id)


def remove_channel_by_(channel_title: str) -> None:
    """Removes channel by the given channel title."""
    with MySession() as session:
        channel = (
            session.query(Channel)
            .filter(Channel.title == channel_title)
            .first()
        )
        session.delete(channel)
        session.commit()
    del channels[channel.user_id]
