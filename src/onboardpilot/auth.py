"""Simple auth helpers."""

from __future__ import annotations

import datetime as dt

import bcrypt
from jose import JWTError, jwt

from onboardpilot.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def create_access_token(subject: str, role: str, name: str) -> str:
    expire = dt.datetime.now(dt.UTC) + dt.timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "role": role, "name": name, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except JWTError:
        return None
