import os
from typing import Any, Callable, Optional, List

from aiogram.types import InputFile

from loader import bot

from .settings import PostSettings


class PostContent:
    """Class for storing post content."""

    def __init__(self) -> None:
        """Initializes the post empty content."""
        self.clear()
        self.target_menu = ""
        self.settings: Optional[PostSettings] = None

    def __iter__(self):
        """Iterates over the post content and yields its items."""
        for content in self.content:
            yield content

    def __len__(self) -> int:
        """Returns the length of the post content."""
        return len(self.content)

    @classmethod
    def from_(cls, post_content_item: dict):
        """Returns the post content from the given post content item."""
        post_content = cls()
        post_content.content.append(post_content_item)
        return post_content

    @property
    def is_there_images(self) -> bool:
        """Returns True if there are images in the post content."""
        return any(content["type"] == "photo" for content in self.content)

    @property
    def images(self) -> List[dict]:
        """Returns the images from the post content."""
        return [
            content for content in self.content if content["type"] == "photo"
        ]

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
            if content["type"] == "photo" and content["content"].startswith(
                "Path:"
            ):
                image_path = content["content"][5:]
                with open(image_path, "rb") as photo:
                    message = await send_function(
                        chat_id, InputFile(photo), **content["kwargs"]
                    )
                os.remove(image_path)
            else:
                message = await send_function(
                    chat_id, content["content"], **content["kwargs"]
                )
            self.message_ids.append(message.message_id)

    # * CRUD methods ----------------------------------------------------------

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

    def update_by_(self, content_item_index: int, content: Any) -> None:
        """Updates content item by the given index."""
        self.content[content_item_index]["content"] = content

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
