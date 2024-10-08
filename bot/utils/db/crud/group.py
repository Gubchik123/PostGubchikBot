from typing import List, Tuple

from .user import groups
from ..db import MySession
from ..models import Channel, Group


def create_group_by_(
    user_chat_id: int,
    group_name: str,
    group_target_menu: str,
    selected_channel_titles: List[str],
) -> None:
    """Creates group by the given
    user chat id, group name, group target menu and selected channel titles."""
    with MySession() as session:
        group = Group(
            name=group_name,
            target_menu=group_target_menu,
            user_id=user_chat_id,
        )
        group.channels.extend(
            session.query(Channel)
            .filter(Channel.title.in_(selected_channel_titles))
            .all()
        )
        session.add(group)
        session.commit()
        groups[group_target_menu].pop(user_chat_id)


def get_group_channel_titles_by_(group_name: str) -> Tuple[str]:
    """Returns group channel titles by the given group name."""
    with MySession() as session:
        return tuple(
            channel.title
            for channel in session.query(Group)
            .filter(Group.name == group_name)
            .first()
            .channels
        )
