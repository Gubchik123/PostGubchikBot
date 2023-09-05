from typing import Callable

from loader import bot


class PostContent:
    """Class for storing post content."""

    def __init__(self) -> None:
        """Initializes the post empty content."""
        self.clear()

    def clear(self) -> None:
        """Clears the post content."""
        self.content = []

    async def send_to_(self, chat_id: int) -> None:
        """Sends the post content to the given chat."""
        for content in self.content:
            send_function: Callable = getattr(bot, f"send_{content['type']}")
            await send_function(chat_id, content["content"])

    def add(self, type: str, content: str) -> None:
        """Adds the content to the post content."""
        self.content.append({"type": type, "content": content})
