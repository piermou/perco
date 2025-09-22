from typing import Any

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.models import User, UserCreate, UserEnd, UserUpdate
from app.security import get_password_hash, validate, verify_password
from config import POSTGRES_URL


# injection FASTapi
def get_db():
    #
    engine = create_engine(POSTGRES_URL, echo=True)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_user(session: Session, user_create: UserCreate) -> UserEnd:
    #
    validate(user_create.password)
    db_obj = user_create.model_dump()
    db_obj.update({"password_hash": get_password_hash(user_create.password)})

    db_user = User(
        username=user_create.username,
        email=user_create.email,
        password_hash=get_password_hash(user_create.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


def get_user(session: Session, email: str) -> UserEnd:
    #
    stmt = select(User).where(User.email == email)
    user = session.scalars(stmt).first()
    return user


def authenticate_user(session: Session, email: str, password: str) -> UserEnd:
    #
    db_user = get_user(session=session, email=email)

    if not db_user:
        raise ValueError("no user link to this email")
    if not verify_password(password, db_user.password_hash):
        raise ValueError("⚠️ Authentication failed")
    print("✅ Authentication succeed")
    return db_user


def update_user(session: Session, db_user: UserEnd, user_in: UserUpdate) -> Any:
    #
    user_data = user_in.model_dump(exclude_unset=True)
    new_password = user_data.pop("password")
    if new_password is not None:
        validate(new_password)
        password_hashed = get_password_hash(new_password)
        db_user.password_hash = password_hashed

    for field, value in user_data.items():
        setattr(db_user, field, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


if __name__ == "__main__":
    pass
