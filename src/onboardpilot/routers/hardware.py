"""Hardware router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import ChecklistItem, HardwareAsset, OnboardingCase
from onboardpilot.deps import get_current_user
from onboardpilot.services.audit import audit

router = APIRouter(prefix="/api", tags=["hardware"])


class HardwareIn(BaseModel):
    case_id: str | None = None
    asset_type: str
    brand_model: str = ""
    serial_number: str = ""
    condition: str = "new"
    handover_date: str = ""
    assigned_employee: str = ""
    return_status: str = "not_returned"
    notes: str = ""


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
def list_hardware(case_id: str | None = None, db=Depends(get_db), user=Depends(get_current_user)):
    q = select(HardwareAsset)
    if case_id:
        q = q.where(HardwareAsset.case_id == case_id)
    return [_to_dict(h) for h in db.execute(q).scalars().all()]


@router.post("/hardware")
def create_hardware(payload: HardwareIn, db=Depends(get_db), user=Depends(get_current_user)):
    h = HardwareAsset(**payload.model_dump())
    db.add(h)
    db.flush()
    # update checklist item for hardware handover if case linked
    if payload.case_id and payload.handover_date:
        items = db.execute(select(ChecklistItem).where(ChecklistItem.case_id == payload.case_id)).scalars().all()
        for it in items:
            if it.key in ("laptop", "monitor", "dock", "headset") and it.key == payload.asset_type and it.status != "completed":
                # only mark if asset_type matches key
                pass
        # mark generic hardware item if exists
        for it in items:
            if it.category == "Hardware" and it.status in ("not_started", "in_progress", "blocked"):
                # mark the first pending hardware item? keep simple: update by asset_type key
                if it.key == payload.asset_type:
                    it.status = "completed"
                    it.completed_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
                    it.completed_by = user.get("name", "operator")
    db.commit()
    audit(user.get("name", "operator"), "hardware_assigned", "hardware", h.id, f"Assigned {h.asset_type} {h.brand_model}", h.case_id)
    return _to_dict(h)


@router.patch("/hardware/{asset_id}")
def update_hardware(asset_id: str, payload: dict, db=Depends(get_db), user=Depends(get_current_user)):
    h = db.get(HardwareAsset, asset_id)
    if not h:
        raise HTTPException(404, "not found")
    for k in ["asset_type", "brand_model", "serial_number", "condition", "handover_date", "assigned_employee", "return_status", "notes", "case_id"]:
        if k in payload:
            setattr(h, k, payload[k])
    db.commit()
    audit(user.get("name", "operator"), "hardware_updated", "hardware", h.id, f"Updated {h.asset_type}", h.case_id)
    return _to_dict(h)


@router.delete("/hardware/{asset_id}")
def delete_hardware(asset_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    h = db.get(HardwareAsset, asset_id)
    if not h:
        raise HTTPException(404, "not found")
    db.delete(h)
    db.commit()
    return {"ok": True}
