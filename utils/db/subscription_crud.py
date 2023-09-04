from datetime import datetime, timedelta

from loader import scheduler
from .user_crud import _get_user_by_
from .models import User, Subscription
from .db import MySession, commit_and_refresh
from utils.scheduler import (
    send_subscription_reminder_to_user,
    remove_user_subscription_by_,
)


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
        user.subscription_expire_date = datetime.today() + timedelta(minutes=6)
        commit_and_refresh(session, user)
    _add_scheduler_jobs_to_remind_user_about_subscription_expire_date(user)
    _add_scheduler_job_to_remove_user_subscription(user)


def _add_scheduler_jobs_to_remind_user_about_subscription_expire_date(
    user: User,
) -> None:
    """Adds scheduler jobs to remind user about subscription expire date."""
    for day in (5, 3, 2, 1):
        scheduler.add_job(
            send_subscription_reminder_to_user,
            trigger="date",
            id=f"{user.chat_id}_{day}_days",
            run_date=user.subscription_expire_date - timedelta(days=day),
            kwargs={
                "user_chat_id": user.chat_id,
                "user_language_code": user.language_code,
                "period_left": day,
                "period_plural_name": "days",
            },
        )
    scheduler.add_job(
        send_subscription_reminder_to_user,
        trigger="date",
        id=f"{user.chat_id}_2_hours",
        run_date=user.subscription_expire_date - timedelta(hours=2),
        kwargs={
            "user_chat_id": user.chat_id,
            "user_language_code": user.language_code,
            "period_left": 2,
            "period_plural_name": "hours",
        },
    )


def _add_scheduler_job_to_remove_user_subscription(user: User) -> None:
    """Adds scheduler job to remove user subscription."""
    scheduler.add_job(
        remove_user_subscription_by_,
        trigger="date",
        id=f"{user.chat_id}_remove_subscription",
        run_date=user.subscription_expire_date,
        kwargs={"user_chat_id": user.chat_id},
    )
