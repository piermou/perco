import logging
import random
import re
import sqlite3
import uuid
from datetime import datetime

import sqlalchemy
import sqlalchemy.exc
from bcrypt import checkpw, gensalt, hashpw
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from config import POSTGRES_URL
from db.models import Base, User
from src.filter import Filter

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

        print("✅ user added with success")
    except sqlalchemy.exc.IntegrityError:
        session.rollback()
        print("email probably already exist")


# insert_user("baby", "baby@gmail.com", "db3A6ffdee!!")


def get_users(email: str):
    stmt = select(User).where(User.email == email)
    user = session.scalars(stmt).first()
    if user is not None:
        print(user.password_hash)
    else:
        raise ValueError("no user link to this email")


# get_users("baby@gmail.com")


def authenticate_user(email: str, password: str):
    stmt = select(User.password_hash).where(User.email == email)
    user_pw = session.scalars(stmt).first()
    print(user_pw, type(user_pw))
    if user_pw and checkpw(password.encode("utf-8"), user_pw.encode("utf-8")):
        print("authentification réussie")
        return True
    print("authentification échouée")
    return False


authenticate_user("baby@gmail.com", "db3A6ffdee!!")

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


# def update_user(user_id, new_email):
#     cursor.execute("UPDATE users SET email = ? WHERE user_id = ?", (new_email, user_id))
#     conn.commit()
#     print("Changement d'email pris en compte")


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
