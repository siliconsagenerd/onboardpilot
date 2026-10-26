"""Audit logging helper."""

from __future__ import annotations

from onboardpilot.db import db_session
from onboardpilot.db.models import AuditLog


def audit(
    actor: str, action: str, entity_type: str, entity_id: str = "", description: str = "", case_id: str | None = None
) -> None:
    with db_session() as db:
        db.add(
            AuditLog(
                actor=actor or "system",
                action=action,
                entity_type=entity_type,
                entity_id=entity_id or "",
                description=description,
                case_id=case_id,
            )
        )
