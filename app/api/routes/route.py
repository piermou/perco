from datetime import datetime, timedelta
from hashlib import sha256
from typing import List

import jwt

# from passlib.context import CryptContext
from bcrypt import checkpw
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from typing_extensions import Annotated

from app.crud import get_db
from app.models import Base, User
from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8000"],  # En production, spécifiez l'origine exacte
#     allow_origin_regex='https://.*\.example\.org'
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


class UserBase(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verif_mdp(plain_password, password_hash):
    return checkpw(plain_password, password_hash)


def get_user(identifier: str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.email == identifier).first()


# def get_usernow(db: Annotated[Session, Depends(get_db)]):
#     return db.query(User).all()


def authenticate_user(identifier, password, db: Session):
    try:
        user = get_user(identifier, db)
        print("merde ici ", user)
        if not user:
            return False
        if not verif_mdp(password, user.password_hash):
            return False
        return user
    except Exception as e:
        print(f"Erreur lors de l'authentification: {e}")
        return False


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        user_id = payload.get("sub")
        print(user_id)
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(user_id, db)
    print(user)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/", response_class=HTMLResponse)
async def accueil(request: Request):
    return templates.TemplateResponse("accueil.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.email)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # Créer la réponse
    response = {"access_token": access_token, "token_type": "bearer"}

    # Définir le cookie
    response_obj = JSONResponse(content=response)
    response_obj.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False,  # Mettre à True en production avec HTTPS
    )

    return response_obj


@app.get("/home", response_class=HTMLResponse)
async def read_users_me(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
):
    return templates.TemplateResponse(
        "home.html", {"request": request, "user_mail": current_user.email}
    )


# @app.post("/test")
# async def test_form(identifier: str = Form(...), password: str = Form(...)):
#     return {"identifier": identifier, "password": password}


# @app.get("/filters", response_model=List[FilterModel])
# async def get_user_filters(
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     user_id = current_user.id
#     user_id = str(user_id)
#     filters = Filter.filters(user_id)
#     # retournera un FilterModel, Filter version pydantic quoi ...
#     return [f.to_pydantic() for f in filters]


# @app.get(
#     "/filters/{filter_name}",
#     response_model=FilterModel,
#     responses={404: {"description": "Ce filtre n'existe pas ..."}},
# )
# async def get_filter(
#     filter_name: str,
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     filters = await get_user_filters(current_user)
#     for f in filters:
#         if f.name == filter_name:
#             return f
#     raise HTTPException(status == 404, detail="Filter not found")


# @app.get("/filters/{filter_name}/feed")
# async def feed_filter(
#     filter_name: str,
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     filter = await get_filter(filter_name, current_user)
#     await alt_main(filter.feed)


# @app.get("/filters/{filter_name}/browse")
# async def browse_filter(
#     filter_name: str,
#     current_user: Annotated[User, Depends(get_current_user)],
# ):
#     filter = await get_filter(filter_name, current_user)
#     await alt_main(filter.browse)


# @app.post("/create_url_filter")
# async def create_url_filter(
#     url: str = Form(...),
#     authorization: Optional[str] = Header(None),
# ):
#     if authorization:
#         try:
#             current_user = await get_current_user(token)
#             user_id = current_user.id
#         except Exception:
#             user_id = 1  # fallback pour dev
#     else:
#         print("RIEN, NADA")
#         user_id = 1

#     mdr = Filter()
#     mdr.id = str(user_id)
#     mdr.add_url(url)  # tu dois définir cette méthode dans Filter

#     return {"message": f"URL ajoutée à {mdr.id}"}


# @app.post("/create_filter/")
# async def create_filter(filter: Filter, current_user: User = Depends(get_current_user)):
#     user_id = current_user.id

#     mdr = Filter()
#     mdr.id = str(user_id)
#     mdr.create_filter(filter.name, filter.criteria)
#     return {"message": "Filter created successfully", "filter": filter}
