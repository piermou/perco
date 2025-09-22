import random
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from config import SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = "HS256"

patterns = [r"[A-Z]", r"[a-z]", r"\d", r"[!@#$%^&*(),.?\":{}|<>]"]


def uuuid_gen(length: int):
    numbers = range(10)
    uuuid = 0
    for i in range(length):
        uuuid += random.choice(numbers) * (10**i)
    return uuuid


def validate(password: str):
    for pattern in patterns:
        if not re.search(pattern, password):
            raise ValueError(f"password must contains {pattern}")
    if len(password) < 12:
        raise ValueError("password must be 12 character min")
    elif len(password) > 30:
        raise ValueError("not going to write a novel, don't you ?")
    else:
        return password


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
