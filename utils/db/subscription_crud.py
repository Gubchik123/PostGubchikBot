from .models import Subscription
from .user_crud import _get_user_by_
from .db import MySession, commit_and_refresh


def get_all_subscriptions() -> list[Subscription]:
    """Returns all subscriptions ordered by id."""
    with MySession() as session:
        return session.query(Subscription).all()


def add_subscription_for_user_with_(
    chat_id: int, subscription_price: int
) -> None:
    """Adds subscription for user with the given chat id."""
    with MySession() as session:
        user = _get_user_by_(session, chat_id)
        user.subscription_id = (
            session.query(Subscription)
            .filter(Subscription.price == subscription_price)
            .first()
            .id
        )
        commit_and_refresh(session, user)
