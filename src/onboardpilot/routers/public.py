"""Public read-only demo router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import AccessRequest, ChecklistItem, HardwareAsset, OnboardingCase, OpenItem
from onboardpilot.routers.access import _to_dict as acc_to_dict
from onboardpilot.routers.cases import _case_to_dict
from onboardpilot.routers.checklist import _item_to_dict
from onboardpilot.routers.hardware import _to_dict as hw_to_dict
from onboardpilot.routers.open_items import _to_dict as oi_to_dict

router = APIRouter(prefix="/api/public", tags=["public"])


def _demo_case(db):
    c = db.execute(select(OnboardingCase).where(OnboardingCase.is_public_demo == True)).scalar_one_or_none()  # noqa: E712
    if not c:
        raise HTTPException(404, "no public demo case")
    return c


@router.get("/demo")
def public_demo(db=Depends(get_db)):
    c = _demo_case(db)
    items = (
        db.execute(select(ChecklistItem).where(ChecklistItem.case_id == c.id).order_by(ChecklistItem.sort_order))
        .scalars()
        .all()
    )
    hardware = db.execute(select(HardwareAsset).where(HardwareAsset.case_id == c.id)).scalars().all()
    access = db.execute(select(AccessRequest).where(AccessRequest.case_id == c.id)).scalars().all()
    open_items = db.execute(select(OpenItem).where(OpenItem.case_id == c.id)).scalars().all()
    from onboardpilot.db.models import AuditLog

    audit = (
        db.execute(select(AuditLog).where(AuditLog.case_id == c.id).order_by(AuditLog.timestamp.desc())).scalars().all()
    )
    return {
        "case": _case_to_dict(c),
        "checklist": [_item_to_dict(i) for i in items],
        "hardware": [hw_to_dict(h) for h in hardware],
        "access": [acc_to_dict(a) for a in access],
        "open_items": [oi_to_dict(o) for o in open_items],
        "audit": [
            {
                "id": a.id,
                "actor": a.actor,
                "action": a.action,
                "description": a.description,
                "timestamp": a.timestamp.isoformat(),
            }
            for a in audit
        ],
    }


@router.get("/guides")
def public_guides(q: str = "", db=Depends(get_db)):
    from onboardpilot.routers.guides import list_guides

    return list_guides(q=q, db=db)
