from typing import List, Tuple

from apscheduler.job import Job

from loader import bot, scheduler

from .post.content import PostContent
from .db.crud.user import get_user_channels_by_, reset_user_subscription_by_


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


def get_user_scheduled_post_jobs_by_(user_chat_id: int) -> Tuple[Job]:
    """Returns user scheduled post jobs by the given user chat id."""
    return tuple(
        job
        for job in scheduler.get_jobs()
        if job.id.startswith(f"{user_chat_id}_post_")
        and "in_queue" not in job.id
    )


def get_user_scheduled_post_in_queue_jobs_by_(user_chat_id: int) -> Tuple[Job]:
    """Returns user scheduled post in queue jobs by the given user chat id."""
    return tuple(
        job
        for job in scheduler.get_jobs()
        if job.id.startswith(f"{user_chat_id}_post_in_queue_")
    )


def get_user_scheduled_post_job_by_(post_id: str, user_chat_id: int) -> Job:
    """
    Returns user scheduled post job by the given post id and user chat id.
    """
    return scheduler.get_job(f"{user_chat_id}_post_{post_id}")


def get_user_scheduled_post_in_queue_job_by_(
    post_id: str, user_chat_id: int
) -> Job:
    """Returns user scheduled post in queue job
    by the given post id and user chat id."""
    return scheduler.get_job(f"{user_chat_id}_post_in_queue_{post_id}")


async def remove_user_subscription_by_(
    user_chat_id: int, user_language_code: str
) -> None:
    """Removes user subscription by the given user chat id."""
    reset_user_subscription_by_(user_chat_id)
    user_scheduled_post_jobs = get_user_scheduled_post_jobs_by_(user_chat_id)
    if user_scheduled_post_jobs:
        _pause_(user_scheduled_post_jobs)
    await bot.send_message(
        user_chat_id,
        text=(
            "Твоя подписка закончилась! Все отложенные посты остановлены!"
            if user_language_code == "ru"
            else "Your subscription has expired! All scheduled posts are paused!"
        ),
    )


def _pause_(user_scheduled_post_jobs: List[Job]) -> None:
    """Pauses all user scheduled post jobs."""
    for job in user_scheduled_post_jobs:
        job.pause()


async def delete_post(channel_chat_id: int, message_ids: List[int]) -> None:
    """Deletes post by the given channel chat id and message ids."""
    for message_id in message_ids:
        await bot.delete_message(channel_chat_id, message_id)


async def publish_user_post(
    author_chat_id: int,
    author_language_code: str,
    post_content: PostContent,
    selected_channels: List[str],
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


async def publish_user_post_in_queue(
    author_chat_id: int,
    author_language_code: str,
    post_content_item: dict,
    selected_channels: List[str],
) -> None:
    """Publishes user post in queue."""
    post_content = PostContent.from_(post_content_item)
    await publish_user_post(
        author_chat_id,
        author_language_code,
        post_content,
        selected_channels,
    )
