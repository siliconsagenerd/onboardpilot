"""Onboarding cases router."""

from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import AuditLog, ChecklistItem, OnboardingCase
from onboardpilot.deps import get_current_user
from onboardpilot.services.audit import audit
from onboardpilot.services.templates import generate_checklist_items

router = APIRouter(prefix="/api/cases", tags=["cases"])

VALID_STATUSES = ["pre_boarding", "hardware_ready", "accounts_provisioned", "orientation_complete", "first_week_support", "completed"]


class CaseIn(BaseModel):
    employee_name: str
    employee_email: str = ""
    role_template: str
    department: str = ""
    start_date: str = ""
    manager_name: str = ""
    manager_email: str = ""


def _case_to_dict(c: OnboardingCase) -> dict:
    return {
        "id": c.id,
        "employee_name": c.employee_name,
        "employee_email": c.employee_email,
        "role_template": c.role_template,
        "department": c.department,
        "start_date": c.start_date,
        "manager_name": c.manager_name,
        "manager_email": c.manager_email,
        "status": c.status,
        "is_public_demo": c.is_public_demo,
        "created_by": c.created_by,
        "created_at": c.created_at.isoformat() if c.created_at else "",
        "updated_at": c.updated_at.isoformat() if c.updated_at else "",
    }


@router.get("")
def list_cases(db=Depends(get_db), user=Depends(get_current_user)):
    cases = db.execute(select(OnboardingCase).order_by(OnboardingCase.created_at.desc())).scalars().all()
    return [_case_to_dict(c) for c in cases]


@router.get("/{case_id}")
def get_case(case_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    c = db.get(OnboardingCase, case_id)
    if not c:
        raise HTTPException(404, "case not found")
    return _case_to_dict(c)


@router.post("")
def create_case(payload: CaseIn, db=Depends(get_db), user=Depends(get_current_user)):
    c = OnboardingCase(
        employee_name=payload.employee_name,
        employee_email=payload.employee_email,
        role_template=payload.role_template,
        department=payload.department,
        start_date=payload.start_date,
        manager_name=payload.manager_name,
        manager_email=payload.manager_email,
        status="pre_boarding",
        created_by=user.get("name", "operator"),
    )
    db.add(c)
    db.flush()
    for item in generate_checklist_items(c.id, payload.role_template, payload.start_date):
        db.add(ChecklistItem(**item))
    db.commit()
    audit(user.get("name", "operator"), "case_created", "case", c.id, f"Created onboarding case for {c.employee_name}", c.id)
    return _case_to_dict(c)


@router.patch("/{case_id}")
def update_case(case_id: str, payload: dict, db=Depends(get_db), user=Depends(get_current_user)):
    c = db.get(OnboardingCase, case_id)
    if not c:
        raise HTTPException(404, "case not found")
    for k in ["employee_name", "employee_email", "department", "start_date", "manager_name", "manager_email", "status"]:
        if k in payload:
            setattr(c, k, payload[k])
    c.updated_at = dt.datetime.now(dt.UTC)
    db.commit()
    audit(user.get("name", "operator"), "case_updated", "case", c.id, f"Updated case {c.employee_name}", c.id)
    return _case_to_dict(c)


@router.delete("/{case_id}")
def delete_case(case_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    c = db.get(OnboardingCase, case_id)
    if not c:
        raise HTTPException(404, "case not found")
    db.delete(c)
    db.commit()
    audit(user.get("name", "operator"), "case_deleted", "case", case_id, f"Deleted case")
    return {"ok": True}
