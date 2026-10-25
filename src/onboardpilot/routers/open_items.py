"""Open items router."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import OpenItem
from onboardpilot.deps import get_current_user, require_role
from onboardpilot.services.audit import audit

router = APIRouter(prefix="/api", tags=["open-items"])

OpenItemPriority = Literal["low", "medium", "high", "critical"]
OpenItemStatus = Literal["open", "in_progress", "resolved"]


class OpenItemIn(BaseModel):
    case_id: str | None = None
    title: str
    description: str = ""
    owner: str = "it_admin"
    due_date: str = ""
    priority: OpenItemPriority = "medium"
    status: OpenItemStatus = "open"


class OpenItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    owner: str | None = None
    due_date: str | None = None
    priority: OpenItemPriority | None = None
    status: OpenItemStatus | None = None


def _to_dict(o: OpenItem) -> dict:
    return {
        "id": o.id,
        "case_id": o.case_id,
        "title": o.title,
        "description": o.description,
        "owner": o.owner,
        "due_date": o.due_date,
        "priority": o.priority,
        "status": o.status,
        "created_at": o.created_at.isoformat() if o.created_at else "",
        "resolved_at": o.resolved_at.isoformat() if o.resolved_at else "",
    }


@router.get("/open-items")
def list_open_items(
    case_id: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    q = select(OpenItem)
    if case_id:
        q = q.where(OpenItem.case_id == case_id)
    q = q.limit(limit).offset(offset)
    return [_to_dict(o) for o in db.execute(q).scalars().all()]


@router.post("/open-items")
def create_open_item(
    payload: OpenItemIn,
    db=Depends(get_db),
    user=Depends(require_role("it_admin", "manager")),
):
    o = OpenItem(**payload.model_dump())
    db.add(o)
    db.commit()
    audit(user.get("name", "operator"), "open_item_created", "open_item", o.id, f"Created open item: {o.title}", o.case_id)
    return _to_dict(o)


@router.patch("/open-items/{item_id}")
def update_open_item(
    item_id: str,
    payload: OpenItemUpdate,
    db=Depends(get_db),
    user=Depends(require_role("it_admin", "manager")),
):
    o = db.get(OpenItem, item_id)
    if not o:
        raise HTTPException(404, "not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(o, key, value)
    if payload.status == "resolved":
        o.resolved_at = datetime.now(timezone.utc)
    db.commit()
    audit(user.get("name", "operator"), "open_item_updated", "open_item", o.id, f"{o.title} -> {o.status}", o.case_id)
    return _to_dict(o)


@router.delete("/open-items/{item_id}")
def delete_open_item(
    item_id: str,
    db=Depends(get_db),
    user=Depends(require_role("it_admin")),
):
    o = db.get(OpenItem, item_id)
    if not o:
        raise HTTPException(404, "not found")
    db.delete(o)
    db.commit()
    return {"ok": True}
