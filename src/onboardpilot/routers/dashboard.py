"""Dashboard router."""

from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import AccessRequest, ChecklistItem, OnboardingCase, OpenItem
from onboardpilot.deps import get_current_user
from onboardpilot.services.permissions import accessible_case_ids

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(db=Depends(get_db), user=Depends(get_current_user)):
    ids = accessible_case_ids(db, user)
    all_cases = db.execute(select(OnboardingCase)).scalars().all()
    if ids is not None:
        cases = [c for c in all_cases if c.id in ids]
    else:
        cases = list(all_cases)
    case_id_set = {c.id for c in cases}
    today = date.today()
    monday = today + timedelta(days=(7 - today.weekday()) % 7)
    if monday == today:
        monday = today
    # upcoming starters: start_date within next 7 days
    upcoming = []
    for c in cases:
        try:
            if c.start_date:
                sd = date.fromisoformat(c.start_date)
                if today <= sd <= today + timedelta(days=7):
                    upcoming.append(c)
        except Exception:
            pass
    incomplete = [c for c in cases if c.status != "completed"]
    overdue_items = []
    for it in db.execute(select(ChecklistItem)).scalars().all():
        if it.case_id not in case_id_set:
            continue
        if it.status != "completed" and it.due_date:
            try:
                if date.fromisoformat(it.due_date) < today:
                    overdue_items.append(it)
            except Exception:
                pass
    # "Blocked" access requests are pending requests that have not progressed.
    blocked_access = [
        a
        for a in db.execute(select(AccessRequest)).scalars().all()
        if a.status == "requested" and a.case_id in case_id_set
    ]
    open_items = [
        o
        for o in db.execute(select(OpenItem)).scalars().all()
        if o.case_id in case_id_set or (ids is None and o.case_id is None)
    ]
    open_by_owner = {}
    for o in open_items:
        if o.status != "resolved":
            open_by_owner[o.owner] = open_by_owner.get(o.owner, 0) + 1
    # avg progress
    progress = []
    for c in cases:
        items = db.execute(select(ChecklistItem).where(ChecklistItem.case_id == c.id)).scalars().all()
        if items:
            done = sum(1 for i in items if i.status == "completed")
            progress.append(done / len(items) * 100)
    avg_progress = round(sum(progress) / len(progress), 1) if progress else 0.0
    return {
        "total_cases": len(cases),
        "incomplete_cases": len(incomplete),
        "completed_cases": len(cases) - len(incomplete),
        "upcoming_starters": [
            {"id": c.id, "name": c.employee_name, "start_date": c.start_date, "role": c.role_template} for c in upcoming
        ],
        "overdue_items_count": len(overdue_items),
        "blocked_access_count": len(blocked_access),
        "open_items_by_owner": open_by_owner,
        "average_progress": avg_progress,
        "open_items_total": len([o for o in open_items if o.status != "resolved"]),
    }
