"""Audit log router."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import AuditLog
from onboardpilot.deps import get_current_user

router = APIRouter(prefix="/api", tags=["audit"])


def _to_dict(a: AuditLog) -> dict:
    return {
        "id": a.id,
        "case_id": a.case_id,
        "actor": a.actor,
        "action": a.action,
        "entity_type": a.entity_type,
        "entity_id": a.entity_id,
        "description": a.description,
        "timestamp": a.timestamp.isoformat() if a.timestamp else "",
    }


@router.get("/audit")
def list_audit(case_id: str | None = None, limit: int = 100, db=Depends(get_db), user=Depends(get_current_user)):
    q = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
    if case_id:
        q = q.where(AuditLog.case_id == case_id)
    return [_to_dict(a) for a in db.execute(q).scalars().all()]
