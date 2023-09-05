from datetime import datetime, timedelta

from sqlalchemy import update

from loader import scheduler
from .user_crud import _get_user_by_
from .models import User, Subscription
from .db import MySession, commit_and_refresh
from data.config import DEFAULT_SUBSCRIPTION_DAYS
from utils.scheduler import (
    send_subscription_reminder_to_user,
    remove_user_subscription_by_,
)

subscriptions = []


def get_all_subscriptions() -> list[Subscription]:
    """Returns all subscriptions ordered by id."""
    if subscriptions:
        return subscriptions
    with MySession() as session:
        all_subscription = session.query(Subscription).all()
    subscriptions.extend(all_subscription)
    return all_subscription


def change_subscription_price_on_(new_price: int, previous_price: int) -> None:
    """Changes subscription price on the given new price."""
    with MySession() as session:
        session.execute(
            update(Subscription)
            .where(Subscription.price == previous_price)
            .values(price=new_price)
        )
        session.commit()
    subscriptions.clear()


def add_subscription_for_user_with_(
    chat_id: int, subscription_price: int
) -> None:
    """Adds subscription for user with the given chat id."""
    with MySession() as session:
        user = _get_user_by_(session, chat_id)
        was_previous_subscription = user.subscription_id
        user.subscription_id = (
            session.query(Subscription)
            .filter(Subscription.price == subscription_price)
            .first()
            .id
        )
        user.subscription_expire_date = datetime.today() + timedelta(
            days=DEFAULT_SUBSCRIPTION_DAYS
        )
        commit_and_refresh(session, user)
    if was_previous_subscription:
        _remove_all_previous_scheduler_jobs_for_user_with_(user.chat_id)
    _add_scheduler_jobs_to_remind_user_about_subscription_expire_date(user)
    _add_scheduler_job_to_remove_user_subscription(user)


def _remove_all_previous_scheduler_jobs_for_user_with_(chat_id: int) -> None:
    """Removes all previous scheduler jobs for user with the given chat id."""
    for day in (5, 3, 2, 1):
        _try_to_remove_scheduler_job_with_id_(f"{chat_id}_{day}_days")
    _try_to_remove_scheduler_job_with_id_(f"{chat_id}_2_hours")
    _try_to_remove_scheduler_job_with_id_(f"{chat_id}_remove_subscription")


def _try_to_remove_scheduler_job_with_id_(id: str) -> None:
    """Tries to remove scheduler job with the given id."""
    try:
        scheduler.remove_job(id)
    except:
        pass


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
        kwargs={
            "user_chat_id": user.chat_id,
            "user_language_code": user.language_code,
        },
    )
