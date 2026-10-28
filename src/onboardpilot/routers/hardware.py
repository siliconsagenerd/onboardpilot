"""Hardware router."""

from __future__ import annotations

from datetime import UTC, datetime
from datetime import date as _date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, model_validator
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import ChecklistItem, HardwareAsset, OnboardingCase
from onboardpilot.deps import get_current_user, require_role
from onboardpilot.services.audit import audit
from onboardpilot.services.permissions import accessible_case_ids, case_accessible

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

    @model_validator(mode="after")
    def _reject_explicit_nulls(self):
        for field in (
            "asset_type",
            "brand_model",
            "serial_number",
            "condition",
            "handover_date",
            "assigned_employee",
            "return_status",
            "notes",
        ):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


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
    ids = accessible_case_ids(db, user)
    if ids is not None:
        if case_id:
            c = db.get(OnboardingCase, case_id)
            if not c or not case_accessible(user, c):
                raise HTTPException(403, "forbidden")
        else:
            if not ids:
                return []
            q = q.where(HardwareAsset.case_id.in_(ids))
    q = q.limit(limit).offset(offset)
    return [_to_dict(h) for h in db.execute(q).scalars().all()]


@router.post("/hardware")
def create_hardware(
    payload: HardwareIn,
    db=Depends(get_db),
    user=Depends(require_role("it_admin")),
):
    if payload.case_id:
        c = db.get(OnboardingCase, payload.case_id)
        if not c:
            raise HTTPException(404, "case not found")
        ids = accessible_case_ids(db, user)
        if ids is not None and payload.case_id not in ids:
            raise HTTPException(403, "forbidden")
    h = HardwareAsset(**payload.model_dump())
    db.add(h)
    db.flush()
    if payload.case_id and payload.handover_date:
        items = db.execute(select(ChecklistItem).where(ChecklistItem.case_id == payload.case_id)).scalars().all()
        for it in items:
            if it.key == payload.asset_type and it.status in ("not_started", "in_progress", "blocked"):
                it.status = "completed"
                it.completed_at = datetime.now(UTC)
                it.completed_by = user.get("name", "operator")
    audit(
        user.get("name", "operator"),
        "hardware_assigned",
        "hardware",
        h.id,
        f"Assigned {h.asset_type} {h.brand_model}",
        h.case_id,
        db=db,
    )
    db.commit()
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
    ids = accessible_case_ids(db, user)
    if ids is not None and h.case_id and h.case_id not in ids:
        raise HTTPException(403, "forbidden")
    data = payload.model_dump(exclude_unset=True)
    # validate case_id if provided
    if "case_id" in data and data["case_id"]:
        c = db.get(OnboardingCase, data["case_id"])
        if not c:
            raise HTTPException(404, "case not found")
        if ids is not None and data["case_id"] not in ids:
            raise HTTPException(403, "forbidden")
    # validate handover_date if present
    if "handover_date" in data and data["handover_date"]:
        try:
            d = _date.fromisoformat(data["handover_date"])
        except ValueError as exc:
            raise HTTPException(400, "invalid handover_date format (expected YYYY-MM-DD)") from exc
        if d > _date.today():
            raise HTTPException(400, "handover_date cannot be in the future")
    for key, value in data.items():
        setattr(h, key, value)
    # sync checklist if handover present
    target_case = h.case_id
    if target_case and h.handover_date:
        items = db.execute(select(ChecklistItem).where(ChecklistItem.case_id == target_case)).scalars().all()
        for it in items:
            if it.key == h.asset_type and it.status in ("not_started", "in_progress", "blocked"):
                it.status = "completed"
                it.completed_at = datetime.now(UTC)
                it.completed_by = user.get("name", "operator")
    audit(
        user.get("name", "operator"),
        "hardware_updated",
        "hardware",
        h.id,
        f"Updated {h.asset_type} {h.brand_model}",
        h.case_id,
        db=db,
    )
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
    ids = accessible_case_ids(db, user)
    if ids is not None and h.case_id and h.case_id not in ids:
        raise HTTPException(403, "forbidden")
    db.delete(h)
    db.commit()
    return {"ok": True}
