from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app import crud, security
from app.api.depends import CurrentUser, SessionDep, Token
from app.models import UserPublic
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(tags=["login"])


@router.post("/loging/access_token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login
    """

    user = crud.authenticate_user(
        session=session, email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password",
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.get("/loging/test_token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    return current_user


@router.post("/password_recovery/{email}")
def recover_password(email: str, session: SessionDep) -> str:
    """
    Password recovery
    """

    user = crud.get_user(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="No email attach to this user.",
        )
