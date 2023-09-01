from aiogram.types import Chat

from .models import Channel
from .db import add_commit_and_refresh


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
