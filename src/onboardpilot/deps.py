"""Shared dependencies."""

from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from onboardpilot.auth import decode_token
from onboardpilot.config import settings
from onboardpilot.db import get_db
from onboardpilot.db.models import User

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db=Depends(get_db),
):
    if not settings.operator_auth_required:
        return {"id": "anon", "role": "it_admin", "name": "Operator", "sub": "anon"}
    if creds is None:
        raise HTTPException(status_code=401, detail="authentication required")
    data = decode_token(creds.credentials)
    if not data:
        raise HTTPException(status_code=401, detail="invalid token")
    user = db.get(User, data.get("sub"))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="inactive or unknown user")
    return {
        "id": user.id,
        "role": user.role,
        "name": user.full_name,
        "sub": user.id,
        "username": user.username,
        "email": user.email,
    }


def require_role(*roles):
    def dep(user=Depends(get_current_user)):
        if user.get("role") not in roles and user.get("role") != "it_admin":
            raise HTTPException(status_code=403, detail="forbidden")
        return user

    return dep
