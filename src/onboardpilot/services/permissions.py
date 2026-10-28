"""Record visibility helpers."""

from __future__ import annotations

from sqlalchemy import select

from onboardpilot.config import settings
from onboardpilot.db.models import OnboardingCase


def is_admin(user: dict) -> bool:
    return user.get("role") == "it_admin" or not settings.operator_auth_required


def case_accessible(user: dict, case) -> bool:
    if is_admin(user):
        return True
    email = (user.get("email") or "").lower()
    role = user.get("role")
    if role == "employee":
        return (case.employee_email or "").lower() == email
    if role == "manager":
        return (case.manager_email or "").lower() == email
    return False


def accessible_case_ids(db, user: dict):
    """Return None for admin (all), else a set of case ids."""
    if is_admin(user):
        return None
    email = (user.get("email") or "").lower()
    role = user.get("role")
    cases = db.execute(select(OnboardingCase)).scalars().all()
    ids = set()
    for c in cases:
        if role == "employee" and (c.employee_email or "").lower() == email:
            ids.add(c.id)
        elif role == "manager" and (c.manager_email or "").lower() == email:
            ids.add(c.id)
    return ids
