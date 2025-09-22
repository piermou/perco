import datetime
import logging
import uuid

from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    create_engine,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql.schema import PrimaryKeyConstraint, UniqueConstraint

from config import POSTGRES_URL

Base = declarative_base()


class PGContext:
    #
    engine = create_engine(POSTGRES_URL, echo=True)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    def __enter__(self):
        self.session = self.Session()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            logging.error(f"Error SQLAlchemy: {exc_value}")
            self.session.rollback()
        self.session.close()


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, nullable=False, default=True)
    is_superuser = Column(Boolean, nullable=False, default=False)

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


class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    password: str | None
    email: EmailStr | None


class UserEnd(UserBase):
    id: uuid.UUID
    password_hash: str


class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(BaseModel):
    data: list[UserPublic]
    count: int


if __name__ == "__main__":
    print(POSTGRES_URL)
    engine = create_engine(POSTGRES_URL)
    Base.metadata.create_all(engine)
