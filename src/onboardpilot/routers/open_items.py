"""Open items router."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, model_validator
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import OnboardingCase, OpenItem
from onboardpilot.deps import get_current_user, require_role
from onboardpilot.services.audit import audit
from onboardpilot.services.permissions import accessible_case_ids

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
    case_id: str | None = None

    @model_validator(mode="after")
    def _reject_explicit_nulls(self):
        for field in ("title", "description", "owner", "due_date", "priority", "status"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


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
    ids = accessible_case_ids(db, user)
    if ids is not None:
        if case_id:
            c = db.get(OnboardingCase, case_id)
            if not c or c.id not in ids:
                raise HTTPException(403, "forbidden")
        else:
            if not ids:
                return []
            q = q.where(OpenItem.case_id.in_(ids))
    q = q.limit(limit).offset(offset)
    return [_to_dict(o) for o in db.execute(q).scalars().all()]


@router.post("/open-items")
def create_open_item(
    payload: OpenItemIn,
    db=Depends(get_db),
    user=Depends(require_role("it_admin", "manager")),
):
    if payload.case_id:
        c = db.get(OnboardingCase, payload.case_id)
        if not c:
            raise HTTPException(404, "case not found")
        ids = accessible_case_ids(db, user)
        if ids is not None and payload.case_id not in ids:
            raise HTTPException(403, "forbidden")
    o = OpenItem(**payload.model_dump())
    db.add(o)
    db.flush()
    audit(
        user.get("name", "operator"),
        "open_item_created",
        "open_item",
        o.id,
        f"Created open item: {o.title}",
        o.case_id,
        db=db,
    )
    db.commit()
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
    if o.case_id:
        c = db.get(OnboardingCase, o.case_id)
        if c:
            # access check via permissions
            from onboardpilot.services.permissions import case_accessible

            if not case_accessible(user, c):
                raise HTTPException(403, "forbidden")
    data = payload.model_dump(exclude_unset=True)
    if "case_id" in data and data["case_id"]:
        c = db.get(OnboardingCase, data["case_id"])
        if not c:
            raise HTTPException(404, "case not found")
        ids = accessible_case_ids(db, user)
        if ids is not None and data["case_id"] not in ids:
            raise HTTPException(403, "forbidden")
    for key, value in data.items():
        setattr(o, key, value)
    if payload.status == "resolved":
        o.resolved_at = datetime.now(UTC)
    elif payload.status in ("open", "in_progress"):
        o.resolved_at = None
    db.flush()
    audit(
        user.get("name", "operator"),
        "open_item_updated",
        "open_item",
        o.id,
        f"{o.title} -> {o.status}",
        o.case_id,
        db=db,
    )
    db.commit()
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
    if o.case_id:
        ids = accessible_case_ids(db, user)
        if ids is not None and o.case_id not in ids:
            raise HTTPException(403, "forbidden")
    db.delete(o)
    db.commit()
    return {"ok": True}
