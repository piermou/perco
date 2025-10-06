from inspect import isfunction
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import BaseModel, ValidationError
from sqlalchemy.event.registry import exc
from sqlalchemy.orm import Session
from typing_extensions import Generator

from app.pydc_models import Token, TokenPayload, UserEnd

# from app.security import ALGORITHM
from config import SECRET_KEY, engine

ALGORITHM = "HS256"


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access_token")


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> UserEnd:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = session.get(UserEnd, token_data.value)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


CurrentUser = Annotated[UserEnd, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> UserEnd:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
