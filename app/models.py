import logging
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session, declarative_base, relationship
from sqlalchemy.sql.schema import PrimaryKeyConstraint, UniqueConstraint

from config import POSTGRES_URL, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    # is_active = Column(Boolean, nullable=False, default=True)
    # is_superuser = Column(Boolean, nullable=False, default=False)

    urls = relationship("Url", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship(
        "Subscription", back_populates="user", cascade="all, delete-orphan"
    )
    likes = relationship("Like", back_populates="user")
    clicks = relationship("Click", back_populates="user")


class Url(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)

    user = relationship("User", back_populates="urls")

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="unique_name_by_user_id"),
        UniqueConstraint("user_id", "url", name="unique_url_by_user_id"),
    )


class Subscription(Base):
    __tablename__ = "subscriptions"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, nullable=False
    )
    stripe_subscription_id = Column(String, nullable=False)
    status = Column(
        Enum("active", "canceled", "trialing", name="subscription_status"),
        nullable=False,
    )
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)

    user = relationship("User", back_populates="subscriptions")


class Like(Base):
    __tablename__ = "likes"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    item_id = Column(BigInteger, nullable=False)

    user = relationship("User", back_populates="likes")

    __table_args__ = (PrimaryKeyConstraint("user_id", "item_id", name="like_relation"),)


class Click(Base):
    __tablename__ = "clicks"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    item_id = Column(BigInteger, nullable=False)

    user = relationship("User", back_populates="clicks")

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "item_id", name="click_relation"),
    )


def init() -> None:
    Base.metadata.create_all(engine)


def main() -> None:
    logger.info("Creating initial data")
    init()
    logger.info("Initial data created")


if __name__ == "__main__":
    print(POSTGRES_URL)
    main()
