from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from aiohttp.helpers import TOKEN
from jinja2 import Template
from jwt import encode
from pydantic import BaseModel

from config import ALGORITHM, FRONT_URL, PROJECT_NAME, RESET_TOKEN_EXPIRES, SECRET_KEY


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(template_name: str, context: dict[str, Any]) -> str:
    #
    template_str = (Path(__file__) / "email-tmp" / template_name).read_text()

    html_content = Template(template_str).render(context)
    return html_content


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    project_name = PROJECT_NAME
    subject = f"{project_name}, - Password recovery for user {email}"
    link = f"{FRONT_URL}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="test_email.html",
        context={
            "project_name": PROJECT_NAME,
            "username": email,
            "valid_hours": RESET_TOKEN_EXPIRES,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    project_name = PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="test_email.html",
        context={
            "project_name": PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": FRONT_URL,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_password_reset_token(email: str) -> str:
    #
    delta = timedelta(hours=48)
    now = datetime.now(timezone.utc)
    expires = now + delta

    exp = expires.timestamp()

    encoded_jwt = encode(
        {"exp": exp, "nbf": now, "sub": email},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return encoded_jwt
