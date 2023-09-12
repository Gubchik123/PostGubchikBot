from typing import Dict, Any


class PostSettings:
    """Class for storing post settings."""

    def __init__(self) -> None:
        """Initializes the post settings."""
        self.clear()

    def clear(self) -> None:
        """Clears the post settings."""
        self.caption = ""
        self.shuffle = False
        self.watermark = None
        self.reply_markup = None
        self.disable_notification = False
        self.disable_web_page_preview = False

    def get_kwargs_by_(self, content_type: str) -> Dict[str, Any]:
        """Returns the kwargs by the given content type."""
        kwargs = {
            "reply_markup": self.reply_markup,
            "disable_notification": self.disable_notification,
        }
        if content_type not in ("message", "video_note", "sticker"):
            kwargs["caption"] = self.caption
        if content_type == "message":
            kwargs["disable_web_page_preview"] = self.disable_web_page_preview
        return kwargs
