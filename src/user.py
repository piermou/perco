import sqlite3
import uuid
from datetime import datetime

from bcrypt import checkpw, gensalt, hashpw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import POSTGRES_URL

engine = create_engine(POSTGRES_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# injection FASTapi
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


conn = sqlite3.connect("users.db")
cursor = conn.cursor()


def insert_user(email, password):
    try:
        password_hash = hashpw(password.encode("utf-8"), gensalt())  # Hachage sécurisé
        id = uuid.uuid4().int & (1 << 63) - 1
        cursor.execute(
            "INSERT INTO users (id, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (id, email, password_hash, datetime.now().strftime("%Y-%m-%d %H")),
        )
        conn.commit()
        print("✅ Utilisateur ajouté avec succès")
    except sqlite3.IntegrityError:
        print("❌ L'email existe déjà")


def get_users():
    cursor.execute("SELECT id, email, password_hash, created_at FROM users")
    for row in cursor.fetchall():
        print(row)


def authenticate_user(email, password):
    cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    if result and checkpw(password.encode("utf-8"), result[0]):
        print("authentification réussie")
        return True
    print("authentification échouée")
    return False


def update_mdp(user_id, old_pw, new_pw):
    cursor.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    if result and checkpw(old_pw.encode("utf-8"), result[0]):
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hashpw(new_pw.encode("utf-8"), gensalt()), user_id),
        )
        conn.commit()
        print("Changement d'email pris en compte")
    else:
        print("Te fou pas de moi")


def update_user(user_id, new_email):
    cursor.execute("UPDATE users SET email = ? WHERE user_id = ?", (new_email, user_id))
    conn.commit()
    print("Changement d'email pris en compte")


def delete_user(user_id):
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    print("Utilisateur out")


if __name__ == "__main__":
    insert_user("admin", "admin")
    # update_mdp(1, "db308!avou34", "db33A5")
    # get_users()

    # authenticate_user("test@example.com", "monMotDePasseSuperSecret")
    # update_user(1, "new_email@example.com")
    # get_users()
    # delete_user(1)
    # get_users()

# --- Fermeture de la connexion ---
cursor.close()
conn.close()


class User:
    def __init__(self) -> None:
        pass
