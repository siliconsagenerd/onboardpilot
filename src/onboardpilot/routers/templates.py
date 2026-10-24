"""Role templates router."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from onboardpilot.deps import get_current_user
from onboardpilot.services.templates import ROLE_TEMPLATES

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("")
def list_templates(user=Depends(get_current_user)):
    return [{"key": k, "label_de": v["label_de"], "label_en": v["label_en"]} for k, v in ROLE_TEMPLATES.items()]
