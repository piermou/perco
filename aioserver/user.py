import asyncio
import logging
import random
import re
import sqlite3
import uuid
from datetime import datetime
from hmac import new
from time import time

import sqlalchemy
import sqlalchemy.exc
from bcrypt import checkpw, gensalt, hashpw
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from config import POSTGRES_URL, many
from db.models import Base, Url, User
from src.filter import Filter
from src.scraper import alt_main

engine = create_engine(POSTGRES_URL, echo=True)
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
session = Session()


def uuuid_gen(length: int):
    numbers = range(10)
    uuuid = 0
    for i in range(length):
        uuuid += random.choice(numbers) * (10**i)
    return uuuid


patterns = [r"[A-Z]", r"[a-z]", r"\d", r"[!@#$%^&*(),.?\":{}|<>]"]


def validate(password: str):
    if len(password) < 12:
        raise ValueError("password must be 12 character min")
    elif len(password) > 30:
        raise ValueError("not going to write a novel, don't you ?")
    for pattern in patterns:
        if not re.search(pattern, password):
            raise ValueError(f"password must contains {pattern}")


"""pourquoi def set_password dans la class User(Base) ?
à la place de session.add,, session,execute ... et conn.commit(), comme avec sqlite"""


# injection FASTapi
def get_db():
    engine = create_engine(POSTGRES_URL, echo=True)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def insert_user(username: str, email: str, password: str):
    #
    validate(password)
    password_hash = hashpw(password.encode("utf-8"), gensalt())
    try:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
        )

        session.add(user)
        session.commit()

        logging.info("✅ user added with success")
    except sqlalchemy.exc.IntegrityError as e:
        session.rollback()
        logging.warning(
            f"error happen for {e}, which is probably the email already used"
        )


def get_user(email: str):
    stmt = select(User).where(User.email == email)
    user = session.scalars(stmt).first()
    if user is not None:
        return user
    else:
        raise ValueError("no user link to this email")


def authenticate_user(email: str, password: str):
    user = get_user(email)
    if checkpw(password.encode("utf-8"), user.password_hash):
        print("authentification réussie")
        return True
    print("authentification échouée")
    return False


# def update_mdp(user_id, old_pw, new_pw):
#     cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
#     result = cursor.fetchone()
#     if result and checkpw(old_pw.encode("utf-8"), result[0]):
#         cursor.execute(
#             "UPDATE users SET password_hash = ? WHERE id = ?",
#             (hashpw(new_pw.encode("utf-8"), gensalt()), user_id),
#         )
#         conn.commit()
#         print("Changement d'email pris en compte")
#     else:
#         print("Te fou pas de moi")


def update_user(email, new_email):
    user = get_user(email)
    user.email = new_email
    session.commit()
    print("Changement d'email pris en compte")


def insert_url(name: str, url: str, email: str):
    user = get_user(email)
    try:
        url = Url(user_id=user.id, name=name, url=url)

        session.add(url)
        session.commit()

        print("url add with success")
    except sqlalchemy.exc.DataError as e:
        logging.error(f"erreur pour {e}")


def get_filter(email: str):
    user = get_user(email)
    stmt = select(Url.url).where(Url.user_id == user.id)
    filter = session.scalars(stmt).all()
    return filter


# oupsi = get_filter("pierre.mssu@gmail.com")
# mena = ["nike", "adidas", "merde"]
# hihi = Filter(id=14532423)
# for i, j in zip(mena, oupsi):
#     hihi.add_url(name=i, url=j)

# print(hihi.browse(page=1))

# b = time()
# asyncio.run(alt_main(hihi.browse(page=1)))
# final = time()
# print(f"Temps d'exécution : {final - b} secondes")

# for i, j in zip(many, name):
#
#     insert_url(name=j, url=i, email="pierre.mssu@gmail.com")

# def delete_user(user_id):
#     cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
#     conn.commit()
#     print("Utilisateur out")


# if __name__ == "__main__":
#     insert_user("admin", "admin")
# update_mdp(1, "db308!avou34", "db33A5")
# get_users()

# authenticate_user("test@example.com", "monMotDePasseSuperSecret")
# update_user(1, "new_email@example.com")
# get_users()
# delete_user(1)
# get_users()

# --- Fermeture de la connexion ---
# cursor.close()
# conn.close()
