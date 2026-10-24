"""Access requests router."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import AccessRequest, OnboardingCase
from onboardpilot.deps import get_current_user
from onboardpilot.services.audit import audit

router = APIRouter(prefix="/api", tags=["access"])

VALID_STATUSES = ["requested", "approved", "provisioned", "verified"]


class AccessIn(BaseModel):
    case_id: str
    access_type: str
    requester: str = ""
    notes: str = ""


def _to_dict(a: AccessRequest) -> dict:
    return {
        "id": a.id,
        "case_id": a.case_id,
        "access_type": a.access_type,
        "status": a.status,
        "requester": a.requester,
        "approver": a.approver,
        "provisioning_owner": a.provisioning_owner,
        "requested_at": a.requested_at.isoformat() if a.requested_at else "",
        "approved_at": a.approved_at.isoformat() if a.approved_at else "",
        "provisioned_at": a.provisioned_at.isoformat() if a.provisioned_at else "",
        "verified_at": a.verified_at.isoformat() if a.verified_at else "",
        "notes": a.notes,
    }


@router.get("/access")
def list_access(case_id: str | None = None, db=Depends(get_db), user=Depends(get_current_user)):
    q = select(AccessRequest)
    if case_id:
        q = q.where(AccessRequest.case_id == case_id)
    return [_to_dict(a) for a in db.execute(q).scalars().all()]


@router.post("/access")
def create_access(payload: AccessIn, db=Depends(get_db), user=Depends(get_current_user)):
    a = AccessRequest(
        case_id=payload.case_id,
        access_type=payload.access_type,
        status="requested",
        requester=payload.requester or user.get("name", "operator"),
        notes=payload.notes,
    )
    db.add(a)
    db.commit()
    audit(user.get("name", "operator"), "access_requested", "access", a.id, f"Requested {a.access_type}", a.case_id)
    return _to_dict(a)


@router.patch("/access/{req_id}")
def update_access(req_id: str, payload: dict, db=Depends(get_db), user=Depends(get_current_user)):
    a = db.get(AccessRequest, req_id)
    if not a:
        raise HTTPException(404, "not found")
    new_status = payload.get("status")
    if new_status and new_status in VALID_STATUSES:
        # enforce order
        order = VALID_STATUSES
        ci = order.index(a.status)
        ni = order.index(new_status)
        if ni <= ci:
            raise HTTPException(400, "cannot revert status")
        if ni != ci + 1:
            raise HTTPException(400, "invalid transition: must progress one step at a time")
        a.status = new_status
        now = datetime.now(timezone.utc)
        if new_status == "approved":
            a.approver = payload.get("approver", user.get("name", "operator"))
            a.approved_at = now
        elif new_status == "provisioned":
            a.provisioning_owner = payload.get("provisioning_owner", user.get("name", "operator"))
            a.provisioned_at = now
        elif new_status == "verified":
            a.verified_at = now
    if "notes" in payload:
        a.notes = payload["notes"]
    if "approver" in payload:
        a.approver = payload["approver"]
    if "provisioning_owner" in payload:
        a.provisioning_owner = payload["provisioning_owner"]
    db.commit()
    audit(user.get("name", "operator"), f"access_{a.status}", "access", a.id, f"{a.access_type} -> {a.status}", a.case_id)
    return _to_dict(a)


@router.delete("/access/{req_id}")
def delete_access(req_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    a = db.get(AccessRequest, req_id)
    if not a:
        raise HTTPException(404, "not found")
    db.delete(a)
    db.commit()
    return {"ok": True}
