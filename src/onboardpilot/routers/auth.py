"""Auth router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from onboardpilot.auth import create_access_token, verify_password
from onboardpilot.db import get_db
from onboardpilot.db.models import User
from onboardpilot.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginIn(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(payload: LoginIn, db=Depends(get_db)):
    user = db.execute(select(User).where(User.username == payload.username)).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="inactive")
    token = create_access_token(user.id, user.role, user.full_name)
    return {"access_token": token, "token_type": "bearer", "role": user.role, "name": user.full_name, "username": user.username}


@router.get("/me")
def me(current=Depends(get_current_user)):
    return current
