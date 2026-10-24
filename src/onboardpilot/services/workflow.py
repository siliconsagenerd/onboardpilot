"""Workflow rules for checklist dependencies."""

from __future__ import annotations

from sqlalchemy import select

from onboardpilot.db.models import ChecklistItem


def dependency_status_map(case_items: list[ChecklistItem]) -> dict[str, ChecklistItem]:
    return {i.key: i for i in case_items}


def can_complete(item: ChecklistItem, case_items: list[ChecklistItem]) -> tuple[bool, str]:
    by_key = dependency_status_map(case_items)
    for dep_key in (item.depends_on or []):
        dep = by_key.get(dep_key)
        if dep is None:
            continue
        if dep.status != "completed":
            return False, f"Blocked: requires '{dep.title_en}' to be completed first."
    return True, ""


def recompute_blocked(items: list[ChecklistItem]) -> None:
    by_key = {i.key: i for i in items}
    for it in items:
        if it.status == "completed":
            continue
        blocked = False
        reason = ""
        for dep_key in (it.depends_on or []):
            dep = by_key.get(dep_key)
            if dep is not None and dep.status != "completed":
                blocked = True
                reason = f"Blocked: requires '{dep.title_en}' to be completed first."
                break
        if blocked:
            it.status = "blocked"
            it.blocked_reason = reason
        else:
            if it.status == "blocked":
                it.status = "not_started"
                it.blocked_reason = ""
