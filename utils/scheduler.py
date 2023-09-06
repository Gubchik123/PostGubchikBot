from loader import bot
from .post_content import PostContent
from .db.user_crud import get_user_channels_by_, reset_user_subscription_by_


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


async def remove_user_subscription_by_(
    user_chat_id: int, user_language_code: str
) -> None:
    """Removes user subscription by the given user chat id."""
    reset_user_subscription_by_(user_chat_id)
    await bot.send_message(
        user_chat_id,
        text=(
            "Твоя подписка закончилась!"
            if user_language_code == "ru"
            else "Your subscription has expired!"
        ),
    )


async def publish_user_post(
    author_chat_id: int,
    author_language_code: str,
    post_content: PostContent,
    selected_channels: list[str],
) -> None:
    """Publishes user post to the selected channels."""
    await bot.send_message(
        author_chat_id,
        text=(
            "Публикую отложенный пост в выбранные каналы..."
            if author_language_code == "ru"
            else "Publishing a scheduled post to the selected channels..."
        ),
    )
    for channel in get_user_channels_by_(author_chat_id):
        if channel.title in selected_channels:
            await post_content.send_to_(channel.chat_id)
    await bot.send_message(
        author_chat_id,
        text=(
            "Опубликовано в каналах: {selected_channels}"
            if author_language_code == "ru"
            else "Published in channels: {selected_channels}"
        ).format(selected_channels=", ".join(selected_channels)),
    )
    post_content.clear()
