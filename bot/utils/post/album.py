from aiogram.types import MediaGroup, InputMedia


class PostAlbum:
    """Class for storing post album."""

    def __init__(self) -> None:
        """Initializes the post empty album."""
        self.clear()

    def clear(self) -> None:
        """Clears the post album."""
        self.album = []
        self.media_type = None

    def get_album(self) -> MediaGroup:
        """Returns the album (MediaGroup)."""
        return MediaGroup(self.album)

    def add(self, input_media: InputMedia) -> None:
        """Adds the input media to the post album."""
        if not self.media_type:
            self.media_type = input_media.type
        self.album.append(input_media)
