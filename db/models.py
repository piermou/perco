import uuid

from sqlalchemy import (
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
from sqlalchemy.orm import declarative_base, relationship

from config import POSTGRES_URL

Base = declarative_base()


class User(Base):
   __tablename__ = "users"

   id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
   username = Column(String, nullable=False)
   email = Column(String, nullable=False, unique=True)
   password_hash = Column(LargeBinary, nullable=False)
   created_at = Column(DateTime, server_default=func.now())

   urls = relationship("Url", back_populates="user", cascade="all, delete-orphan")
   subscriptions = relationship(
      "Subscription", back_populates="user", cascade="all, delete-orphan"
   )
   favourites = relationship("Favourite", back_populates="user")


class Url(Base):
   __tablename__ = "urls"

   user_id = Column(
      UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, nullable=False
   )
   name = Column(String, nullable=False)
   url = Column(String, nullable=False)

   users = relationship("User", back_populates="urls")


class Subscription(Base):
   __tablename__ = "subscriptions"

   user_id = Column(
      UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, nullable=False
   )
   stripe_subscription_id = Column(String, nullable=False)
   status = Column(
      Enum("active", "canceled", "trialing", name="subscription_status"), nullable=False
   )
   current_period_start = Column(DateTime)
   current_period_end = Column(DateTime)


class Favourite(Base):
   __tablename__ = "favourites"

   user_id = Column(
      UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, nullable=False
   )
   item_id = Column(Integer, nullable=False)

   users = relationship("User", back_populates="favourites")


if __name__ == "__main__":
   print(POSTGRES_URL)
   engine = create_engine(POSTGRES_URL)
   Base.metadata.create_all(engine)
