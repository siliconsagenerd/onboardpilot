"""Audit log router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import AuditLog
from onboardpilot.deps import get_current_user
from onboardpilot.services.permissions import accessible_case_ids

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
    ids = accessible_case_ids(db, user)
    if case_id:
        if ids is not None and case_id not in ids:
            raise HTTPException(403, "forbidden")
        q = q.where(AuditLog.case_id == case_id)
    elif ids is not None:
        if not ids:
            return []
        q = q.where(AuditLog.case_id.in_(ids))
    return [_to_dict(a) for a in db.execute(q).scalars().all()]
