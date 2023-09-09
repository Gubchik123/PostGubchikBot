from datetime import datetime
from pytz import timezone as tz

from sqlalchemy.orm import relationship, backref
from sqlalchemy import (
    Table,
    Column,
    Integer,
    BigInteger,
    String,
    DateTime,
    ForeignKey,
)

from .db import Base
from data.config import (
    DEFAULT_SUBSCRIPTION_DAYS,
    DEFAULT_LANGUAGE_CODE,
    DEFAULT_TIMEZONE,
)


class User(Base):
    """Model for storing information about Telegram users."""

    __tablename__ = "users"
    # Fields from telegram user
    chat_id = Column(BigInteger, primary_key=True, autoincrement=False)
    username = Column(String(32), nullable=True, unique=True)
    full_name = Column(String(110), nullable=False, unique=True)
    # Settings fields
    language_code = Column(
        String(2), nullable=False, default=DEFAULT_LANGUAGE_CODE
    )
    timezone = Column(String(32), nullable=False, default=DEFAULT_TIMEZONE)
    created = Column(DateTime, default=datetime.now(tz(DEFAULT_TIMEZONE)))
    # Referrals fields
    referrals = Column(Integer, default=0)
    balance = Column(Integer, default=0)
    # User channels
    channels = relationship(
        "Channel",
        backref=backref("user", lazy="joined"),
        lazy="dynamic",
        passive_deletes=True,
    )
    # User groups
    groups = relationship(
        "Group",
        backref=backref("user", lazy="joined"),
        lazy="dynamic",
        passive_deletes=True,
    )
    # Subscription fields
    subscription = relationship(
        "Subscription",
        backref=backref("user", lazy="joined"),
        lazy="joined",
        uselist=False,
        passive_deletes=True,
    )
    subscription_id = Column(
        Integer, ForeignKey("subscriptions.id", ondelete="SET NULL")
    )
    subscription_expire_date = Column(DateTime, nullable=True)


class Subscription(Base):
    """Model for storing information about subscriptions."""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    name = Column(String(10), unique=True, nullable=False)
    price = Column(Integer, unique=True, nullable=False)
    max_channels = Column(Integer, unique=True, nullable=True)
    duration_days = Column(Integer, default=DEFAULT_SUBSCRIPTION_DAYS)
    created = Column(DateTime, default=datetime.now(tz(DEFAULT_TIMEZONE)))


# Table for many-to-many relationship between channels and groups
channel_groups = Table(
    "channel_groups",
    Base.metadata,
    Column("channel_id", Integer, ForeignKey("channels.chat_id")),
    Column("group_id", Integer, ForeignKey("groups.id")),
)


class Channel(Base):
    """Model for storing information about Telegram channels."""

    __tablename__ = "channels"

    chat_id = Column(BigInteger, primary_key=True, autoincrement=False)
    title = Column(String(128), nullable=True)
    username = Column(String(32), nullable=True, unique=True)
    bio = Column(String(140), nullable=True)
    description = Column(String(255), nullable=True)

    user_id = Column(
        Integer,
        ForeignKey("users.chat_id", ondelete="CASCADE"),
        nullable=False,
    )
    groups = relationship(
        "Group", secondary=channel_groups, back_populates="channels"
    )


class Group(Base):
    """Model for storing information about channel groups."""

    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    target_menu = Column(
        String(13), nullable=False
    )  # "post creation" or "post in queue"

    user_id = Column(
        Integer,
        ForeignKey("users.chat_id", ondelete="CASCADE"),
        nullable=False,
    )
    channels = relationship(
        "Channel", secondary=channel_groups, back_populates="groups"
    )
