import uuid

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool = True
    is_superuser: bool = False

    class Config:
        from_attributes = True


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


# Payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Content of JWT
class TokenPayload(BaseModel):
    value: str | None = None
