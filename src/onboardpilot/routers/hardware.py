"""Hardware router."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import ChecklistItem, HardwareAsset, OnboardingCase
from onboardpilot.deps import get_current_user, require_role
from onboardpilot.services.audit import audit

router = APIRouter(prefix="/api", tags=["hardware"])

HardwareCondition = Literal["new", "good", "fair", "needs_repair"]
ReturnStatus = Literal["not_returned", "returned"]


class HardwareIn(BaseModel):
    case_id: str | None = None
    asset_type: str
    brand_model: str = ""
    serial_number: str = ""
    condition: HardwareCondition = "new"
    handover_date: str = ""
    assigned_employee: str = ""
    return_status: ReturnStatus = "not_returned"
    notes: str = ""


class HardwareUpdate(BaseModel):
    case_id: str | None = None
    asset_type: str | None = None
    brand_model: str | None = None
    serial_number: str | None = None
    condition: HardwareCondition | None = None
    handover_date: str | None = None
    assigned_employee: str | None = None
    return_status: ReturnStatus | None = None
    notes: str | None = None


def _to_dict(h: HardwareAsset) -> dict:
    return {
        "id": h.id,
        "case_id": h.case_id,
        "asset_type": h.asset_type,
        "brand_model": h.brand_model,
        "serial_number": h.serial_number,
        "condition": h.condition,
        "handover_date": h.handover_date,
        "assigned_employee": h.assigned_employee,
        "return_status": h.return_status,
        "notes": h.notes,
        "created_at": h.created_at.isoformat() if h.created_at else "",
    }


@router.get("/hardware")
def list_hardware(
    case_id: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    q = select(HardwareAsset)
    if case_id:
        q = q.where(HardwareAsset.case_id == case_id)
    q = q.limit(limit).offset(offset)
    return [_to_dict(h) for h in db.execute(q).scalars().all()]


@router.post("/hardware")
def create_hardware(
    payload: HardwareIn,
    db=Depends(get_db),
    user=Depends(require_role("it_admin")),
):
    h = HardwareAsset(**payload.model_dump())
    db.add(h)
    db.flush()
    if payload.case_id and payload.handover_date:
        items = db.execute(select(ChecklistItem).where(ChecklistItem.case_id == payload.case_id)).scalars().all()
        for it in items:
            if it.key == payload.asset_type and it.status in ("not_started", "in_progress", "blocked"):
                it.status = "completed"
                it.completed_at = datetime.now(timezone.utc)
                it.completed_by = user.get("name", "operator")
    db.commit()
    audit(user.get("name", "operator"), "hardware_assigned", "hardware", h.id, f"Assigned {h.asset_type} {h.brand_model}", h.case_id)
    return _to_dict(h)


@router.patch("/hardware/{asset_id}")
def update_hardware(
    asset_id: str,
    payload: HardwareUpdate,
    db=Depends(get_db),
    user=Depends(require_role("it_admin")),
):
    h = db.get(HardwareAsset, asset_id)
    if not h:
        raise HTTPException(404, "not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(h, key, value)
    db.commit()
    return _to_dict(h)


@router.delete("/hardware/{asset_id}")
def delete_hardware(
    asset_id: str,
    db=Depends(get_db),
    user=Depends(require_role("it_admin")),
):
    h = db.get(HardwareAsset, asset_id)
    if not h:
        raise HTTPException(404, "not found")
    db.delete(h)
    db.commit()
    return {"ok": True}
