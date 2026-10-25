"""Checklist router."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import ChecklistItem, OnboardingCase
from onboardpilot.deps import get_current_user, require_role
from onboardpilot.services.audit import audit
from onboardpilot.services.workflow import can_complete, recompute_blocked

router = APIRouter(prefix="/api", tags=["checklist"])

ChecklistStatus = Literal["not_started", "in_progress", "completed", "blocked"]


class ItemUpdate(BaseModel):
    status: ChecklistStatus | None = None
    blocked_reason: str | None = None


def _item_to_dict(i: ChecklistItem) -> dict:
    return {
        "id": i.id,
        "case_id": i.case_id,
        "key": i.key,
        "title_de": i.title_de,
        "title_en": i.title_en,
        "description_de": i.description_de,
        "description_en": i.description_en,
        "category": i.category,
        "owner": i.owner,
        "status": i.status,
        "due_date": i.due_date,
        "depends_on": i.depends_on or [],
        "blocked_reason": i.blocked_reason,
        "completed_at": i.completed_at.isoformat() if i.completed_at else "",
        "completed_by": i.completed_by,
        "sort_order": i.sort_order,
    }


@router.get("/cases/{case_id}/checklist")
def get_checklist(
    case_id: str,
    limit: int = Query(500, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    items = db.execute(
        select(ChecklistItem)
        .where(ChecklistItem.case_id == case_id)
        .order_by(ChecklistItem.sort_order)
        .limit(limit)
        .offset(offset)
    ).scalars().all()
    return [_item_to_dict(i) for i in items]


@router.patch("/checklist/{item_id}")
def update_item(
    item_id: str,
    payload: ItemUpdate,
    db=Depends(get_db),
    user=Depends(require_role("it_admin", "manager")),
):
    item = db.get(ChecklistItem, item_id)
    if not item:
        raise HTTPException(404, "item not found")
    case_items = db.execute(select(ChecklistItem).where(ChecklistItem.case_id == item.case_id)).scalars().all()
    if payload.status == "completed":
        ok, reason = can_complete(item, case_items)
        if not ok:
            raise HTTPException(400, reason)
        item.status = "completed"
        item.blocked_reason = ""
        item.completed_at = datetime.now(timezone.utc)
        item.completed_by = user.get("name", "operator")
        action = "item_completed"
    elif payload.status:
        item.status = payload.status
        item.blocked_reason = payload.blocked_reason or ""
        action = "item_updated"
    else:
        if payload.blocked_reason is not None:
            item.blocked_reason = payload.blocked_reason
        action = "item_updated"
    db.flush()
    refreshed = db.execute(select(ChecklistItem).where(ChecklistItem.case_id == item.case_id)).scalars().all()
    recompute_blocked(refreshed)
    db.commit()
    audit(user.get("name", "operator"), action, "checklist", item.id, f"{item.title_en} -> {item.status}", item.case_id)
    return _item_to_dict(item)


@router.post("/checklist/{item_id}/reopen")
def reopen_item(
    item_id: str,
    db=Depends(get_db),
    user=Depends(require_role("it_admin", "manager")),
):
    item = db.get(ChecklistItem, item_id)
    if not item:
        raise HTTPException(404, "item not found")
    item.status = "not_started"
    item.completed_at = None
    item.completed_by = ""
    item.blocked_reason = ""
    db.flush()
    refreshed = db.execute(select(ChecklistItem).where(ChecklistItem.case_id == item.case_id)).scalars().all()
    recompute_blocked(refreshed)
    db.commit()
    audit(user.get("name", "operator"), "item_reopened", "checklist", item.id, f"Reopened {item.title_en}", item.case_id)
    return _item_to_dict(item)
