from loader import bot


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
