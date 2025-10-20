from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

import config
from app import crud, security
from app.api.depends import (
    CurrentUser,
    SessionDep,
    Token,
    get_current_active_superuser,
)
from app.pydc_models import NewPassword, UserPublic
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    verify_password_reset_token,
)

router = APIRouter(tags=["login"])


@router.post("/login/access_token")
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
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.get("/login/test_token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    return current_user


@router.post("/password_recovery/{email}")  # THIS ONE IS NOT FINISHED YET !!
def recover_password(email: str, session: SessionDep):
    """
    Password recovery
    """

    user = crud.get_user(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="No email attach to this user.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    print("Password recovery email sent")
    return email_data


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> str:
    """
    Reset password
    """

    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.get_user(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404, detail="The user with this email does not exist."
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = security.get_password_hash(password=body.new_password)
    user.password_hash = hashed_password
    session.add(user)
    session.commit()
    return "Password updated successfully"


@router.get(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """

    user = crud.get_user(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404, detail="The user with this username does not exist."
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
