from loader import bot
from utils.db.user_crud import _get_user_by_
from utils.db.db import MySession, commit_and_refresh


async def send_subscription_reminder_to_user(
    user_chat_id: int,
    user_language_code: str,
    period_left: int,
    period_plural_name: str,
) -> None:
    """
    Sends subscription reminder to user about the subscription.

    Args:
        period_left - number of days or hours.
        period_plural_name - 'days' or 'hours'.
    """
    if user_language_code == "ru":
        period_plural_name = {
            "days": "дней",
            "hours": "часов",
        }.get(period_plural_name, period_plural_name)
    await bot.send_message(
        user_chat_id,
        text=(
            f"Твоя подписка закончится через {period_left} {period_plural_name}!"
            if user_language_code == "ru"
            else f"Your subscription will expire in {period_left} {period_plural_name}!"
        ),
    )


async def remove_user_subscription_by_(user_chat_id: int) -> None:
    """Removes user subscription by the given user chat id."""
    with MySession() as session:
        user = _get_user_by_(session, user_chat_id)
        if user and user.subscription:
            user.subscription = None
            user.subscription_expire_date = None
            commit_and_refresh(session, user)
    await bot.send_message(
        user_chat_id,
        text=(
            "Твоя подписка закончилась!"
            if user.language_code == "ru"
            else "Your subscription has expired!"
        ),
    )
