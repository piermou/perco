import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select

from app import crud
from app.api.depends import CurrentUser, SessionDep, get_current_active_superuser
from app.models import User
from app.pydc_models import UserBase, UserCreate, UserPublic, UsersPublic
from app.utils import generate_new_account_email

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count_statement = select(func.count()).select_from(User)
    count = session.execute(count_statement).scalar_one()

    stmt = select(User).offset(skip).limit(limit)
    [users] = session.execute(stmt).scalars().all()

    return UsersPublic(data=users, count=count)


@router.post(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def create_users(session: SessionDep, user_in: UserCreate) -> Any:
    """
    Create user. who could have known
    """
    user = crud.get_user(email=user_in.email, session=session)

    if user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exist.",
        )

    user = crud.create_user(session=session, user_create=user_in)

    if user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email,
            username=user_in.username,
            password=user_in.password,
        )
        print(email_data)
        # send_email() function just right here
    return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    session: SessionDep,
    user_in: UserBase,
    current_user: CurrentUser,
) -> Any:
    pass


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    user = session.get(User, user_id)

    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user
