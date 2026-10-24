"""Guides router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import Guide
from onboardpilot.deps import get_current_user

router = APIRouter(prefix="/api/guides", tags=["guides"])


def _to_dict(g: Guide) -> dict:
    return {
        "id": g.id,
        "slug": g.slug,
        "title_de": g.title_de,
        "title_en": g.title_en,
        "content_de": g.content_de,
        "content_en": g.content_en,
        "category": g.category,
    }


@router.get("")
def list_guides(q: str = "", db=Depends(get_db)):
    stmt = select(Guide)
    guides = db.execute(stmt).scalars().all()
    if q:
        ql = q.lower()
        guides = [g for g in guides if ql in (g.title_de + g.title_en + g.content_de + g.content_en).lower()]
    return [_to_dict(g) for g in guides]


@router.get("/{slug}")
def get_guide(slug: str, db=Depends(get_db)):
    g = db.execute(select(Guide).where(Guide.slug == slug)).scalar_one_or_none()
    if not g:
        raise HTTPException(404, "not found")
    return _to_dict(g)
