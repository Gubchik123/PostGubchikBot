from typing import Any, Callable, Optional

from loader import bot


class PostContent:
    """Class for storing post content."""

    def __init__(self) -> None:
        """Initializes the post empty content."""
        self.clear()
        self.target_menu = ""

    def __iter__(self):
        """Iterates over the post content and yields its items."""
        for content in self.content:
            yield content

    def __len__(self) -> int:
        """Returns the length of the post content."""
        return len(self.content)

    def clear(self) -> None:
        """Clears the post content."""
        self.content = []
        self.clear_message_ids()

    def clear_message_ids(self) -> None:
        """Clears the message ids."""
        self.message_ids = []

    async def send_to_(self, chat_id: int) -> None:
        """Sends the post content to the given chat."""
        for content in self.content:
            if content["type"] == "album":
                await bot.send_media_group(chat_id, media=content["content"])
                break
            send_function: Callable = getattr(bot, f"send_{content['type']}")
            message = await send_function(
                chat_id, content["content"], **content["kwargs"]
            )
            self.message_ids.append(message.message_id)

    def add(self, type: str, content: str) -> dict:
        """Adds the content to the post content and returns its index."""
        content_item = {
            "index": len(self.content),
            "type": type,
            "content": content,
            "kwargs": {},
        }
        self.content.append(content_item)
        return content_item

    def get_item_by_(self, content_index: int) -> dict:
        """Returns content item by the given index."""
        return self.content[content_index]

    def update_kwargs(
        self, content_index: int, key: str, value: Optional[Any] = None
    ) -> dict:
        """Updates kwargs of the content item by the given index."""
        content_item = self.content[content_index]
        if value is None:
            content_item["kwargs"][key] = not self.content[content_index][
                "kwargs"
            ].get(key)
        else:
            content_item["kwargs"][key] = value
        return content_item

    def remove_by_(self, content_index: int) -> None:
        """Removes content by the given index."""
        self.content.pop(content_index)
