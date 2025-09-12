import re
import uuid
from datetime import datetime

from bcrypt import checkpw, gensalt, hashpw
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    MetaData,
    String,
    Uuid,
    create_engine,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from config import POSTGRES_URL

Base = declarative_base()
meta = MetaData()

# id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    urls = relationship("Url", back_populates="user", cascade="all, delete-orphan")


class Url(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="urls")


# class Subscription(Base):
#     __tablename__ = "subs"

#     user_id = Column(Uuid, ForeignKey("users.id"), nullable=False)
#     stripe_sub = Column(String, unique=True, nullable=False)
#     status = Column(String, nullable=False)
#     current_period_start = Column(DateTime)
#     current_period_end = Column(DateTime)


# print(POSTGRES_URL)
# engine = create_engine(POSTGRES_URL)
# Base.metadata.create_all(engine)
# Base.metadata.create_all(engine)
