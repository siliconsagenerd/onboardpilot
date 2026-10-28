"""Access requests router."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, model_validator
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import AccessRequest, OnboardingCase
from onboardpilot.deps import get_current_user, require_role
from onboardpilot.services.audit import audit
from onboardpilot.services.permissions import accessible_case_ids

router = APIRouter(prefix="/api", tags=["access"])

AccessStatus = Literal["requested", "approved", "provisioned", "verified"]


class AccessIn(BaseModel):
    case_id: str
    access_type: str
    requester: str = ""
    notes: str = ""


class AccessUpdate(BaseModel):
    status: AccessStatus | None = None
    notes: str | None = None
    approver: str | None = None
    provisioning_owner: str | None = None

    @model_validator(mode="after")
    def _reject_explicit_nulls(self):
        for field in ("status", "notes", "approver", "provisioning_owner"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


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
def list_access(
    case_id: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    q = select(AccessRequest)
    if case_id:
        q = q.where(AccessRequest.case_id == case_id)
    ids = accessible_case_ids(db, user)
    if ids is not None:
        if case_id:
            c = db.get(OnboardingCase, case_id)
            if not c or c.id not in ids:
                raise HTTPException(403, "forbidden")
        else:
            if not ids:
                return []
            q = q.where(AccessRequest.case_id.in_(ids))
    q = q.limit(limit).offset(offset)
    return [_to_dict(a) for a in db.execute(q).scalars().all()]


@router.post("/access")
def create_access(
    payload: AccessIn,
    db=Depends(get_db),
    user=Depends(require_role("it_admin", "manager")),
):
    c = db.get(OnboardingCase, payload.case_id)
    if not c:
        raise HTTPException(404, "case not found")
    ids = accessible_case_ids(db, user)
    if ids is not None and payload.case_id not in ids:
        raise HTTPException(403, "forbidden")
    a = AccessRequest(
        case_id=payload.case_id,
        access_type=payload.access_type,
        status="requested",
        requester=payload.requester or user.get("name", "operator"),
        notes=payload.notes,
    )
    db.add(a)
    db.flush()
    audit(
        user.get("name", "operator"), "access_requested", "access", a.id, f"{a.access_type} requested", a.case_id, db=db
    )
    db.commit()
    return _to_dict(a)


@router.patch("/access/{req_id}")
def update_access(
    req_id: str,
    payload: AccessUpdate,
    db=Depends(get_db),
    user=Depends(require_role("it_admin", "manager")),
):
    a = db.get(AccessRequest, req_id)
    if not a:
        raise HTTPException(404, "not found")
    # access check
    c = db.get(OnboardingCase, a.case_id)
    if c:
        from onboardpilot.services.permissions import case_accessible

        if not case_accessible(user, c):
            raise HTTPException(403, "forbidden")
    statuses = ["requested", "approved", "provisioned", "verified"]
    if payload.status and payload.status != a.status:
        ci = statuses.index(a.status)
        ni = statuses.index(payload.status)
        if ni < ci:
            raise HTTPException(400, "cannot revert status")
        if ni != ci + 1:
            raise HTTPException(400, "invalid transition: must progress one step at a time")
        a.status = payload.status
        now = datetime.now(UTC)
        if payload.status == "approved":
            a.approver = payload.approver or user.get("name", "operator")
            a.approved_at = now
        elif payload.status == "provisioned":
            a.provisioning_owner = payload.provisioning_owner or user.get("name", "operator")
            a.provisioned_at = now
        elif payload.status == "verified":
            a.verified_at = now
    if payload.notes is not None:
        a.notes = payload.notes
    if payload.approver is not None:
        a.approver = payload.approver
    if payload.provisioning_owner is not None:
        a.provisioning_owner = payload.provisioning_owner
    db.flush()
    audit(
        user.get("name", "operator"),
        f"access_{a.status}",
        "access",
        a.id,
        f"{a.access_type} -> {a.status}",
        a.case_id,
        db=db,
    )
    db.commit()
    return _to_dict(a)


@router.delete("/access/{req_id}")
def delete_access(
    req_id: str,
    db=Depends(get_db),
    user=Depends(require_role("it_admin")),
):
    a = db.get(AccessRequest, req_id)
    if not a:
        raise HTTPException(404, "not found")
    db.delete(a)
    db.commit()
    return {"ok": True}
