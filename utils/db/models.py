from datetime import datetime

from sqlalchemy.orm import relationship, backref
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
)

from .db import Base
from data.config import DEFAULT_LANGUAGE_CODE, DEFAULT_TIMEZONE


class User(Base):
    """Model for storing information about Telegram users."""

    __tablename__ = "user"

    chat_id = Column(BigInteger, primary_key=True, autoincrement=False)
    username = Column(String(32), nullable=False, unique=True)
    full_name = Column(String(110), nullable=False, unique=True)
    language_code = Column(
        String(2), nullable=False, default=DEFAULT_LANGUAGE_CODE
    )
    time_zone = Column(String(32), nullable=False, default=DEFAULT_TIMEZONE)
    created = Column(DateTime, default=datetime.today())

    channels = relationship(
        "Channel",
        backref=backref("user", lazy="joined"),
        lazy="dynamic",
        passive_deletes=True,
    )


class Channel(Base):
    """Model for storing information about Telegram channels."""

    __tablename__ = "channel"

    chat_id = Column(BigInteger, primary_key=True, autoincrement=False)
    title = Column(String(128), nullable=True)
    username = Column(String(32), nullable=True, unique=True)
    bio = Column(String(140), nullable=True)
    description = Column(String(255), nullable=True)

    user_id = Column(
        Integer, ForeignKey("user.chat_id", ondelete="CASCADE"), nullable=False
    )
