"""Shared dependencies."""

from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from onboardpilot.auth import decode_token
from onboardpilot.config import settings

bearer = HTTPBearer(auto_error=False)


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    if not settings.operator_auth_required:
        return {"id": "anon", "role": "it_admin", "name": "Operator", "sub": "anon"}
    if creds is None:
        raise HTTPException(status_code=401, detail="authentication required")
    data = decode_token(creds.credentials)
    if not data:
        raise HTTPException(status_code=401, detail="invalid token")
    return data


def require_role(*roles):
    def dep(user=Depends(get_current_user)):
        if user.get("role") not in roles and user.get("role") != "it_admin":
            raise HTTPException(status_code=403, detail="forbidden")
        return user

    return dep
