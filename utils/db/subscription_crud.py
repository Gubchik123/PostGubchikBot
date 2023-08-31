from .db import MySession
from .models import Subscription


def get_all_subscriptions() -> list[Subscription]:
    """Returns all subscriptions ordered by id."""
    with MySession() as session:
        return session.query(Subscription).all()
