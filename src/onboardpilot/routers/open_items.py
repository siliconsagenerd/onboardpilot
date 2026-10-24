"""Open items router."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import OpenItem
from onboardpilot.deps import get_current_user
from onboardpilot.services.audit import audit

router = APIRouter(prefix="/api", tags=["open-items"])


class OpenItemIn(BaseModel):
    case_id: str | None = None
    title: str
    description: str = ""
    owner: str = "it_admin"
    due_date: str = ""
    priority: str = "medium"
    status: str = "open"


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
def list_open_items(case_id: str | None = None, db=Depends(get_db), user=Depends(get_current_user)):
    q = select(OpenItem)
    if case_id:
        q = q.where(OpenItem.case_id == case_id)
    return [_to_dict(o) for o in db.execute(q).scalars().all()]


@router.post("/open-items")
def create_open_item(payload: OpenItemIn, db=Depends(get_db), user=Depends(get_current_user)):
    o = OpenItem(**payload.model_dump())
    db.add(o)
    db.commit()
    audit(user.get("name", "operator"), "open_item_created", "open_item", o.id, f"Created open item: {o.title}", o.case_id)
    return _to_dict(o)


@router.patch("/open-items/{item_id}")
def update_open_item(item_id: str, payload: dict, db=Depends(get_db), user=Depends(get_current_user)):
    o = db.get(OpenItem, item_id)
    if not o:
        raise HTTPException(404, "not found")
    for k in ["title", "description", "owner", "due_date", "priority", "status"]:
        if k in payload:
            setattr(o, k, payload[k])
    if payload.get("status") == "resolved":
        o.resolved_at = datetime.now(timezone.utc)
    db.commit()
    audit(user.get("name", "operator"), "open_item_updated", "open_item", o.id, f"{o.title} -> {o.status}", o.case_id)
    return _to_dict(o)


@router.delete("/open-items/{item_id}")
def delete_open_item(item_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    o = db.get(OpenItem, item_id)
    if not o:
        raise HTTPException(404, "not found")
    db.delete(o)
    db.commit()
    return {"ok": True}
