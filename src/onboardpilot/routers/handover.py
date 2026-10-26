"""Handover protocol PDF router."""

from __future__ import annotations

import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fpdf import FPDF
from sqlalchemy import select

from onboardpilot.db import get_db
from onboardpilot.db.models import AccessRequest, ChecklistItem, HardwareAsset, OnboardingCase, OpenItem
from onboardpilot.deps import get_current_user

router = APIRouter(prefix="/api", tags=["handover"])


def build_pdf(case, items, hardware, access, open_items) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "OnboardPilot - IT Handover Protocol", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Employee: {case.employee_name}", ln=True)
    pdf.cell(0, 8, f"Role: {case.role_template}", ln=True)
    pdf.cell(0, 8, f"Department: {case.department}", ln=True)
    pdf.cell(0, 8, f"Start date: {case.start_date}", ln=True)
    pdf.cell(0, 8, f"Manager: {case.manager_name}", ln=True)
    pdf.cell(0, 8, f"Status: {case.status}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Hardware", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for h in hardware:
        pdf.cell(
            0,
            6,
            f"- {h.asset_type}: {h.brand_model} (SN: {h.serial_number}) - {h.handover_date} - {h.return_status}",
            ln=True,
        )
    if not hardware:
        pdf.cell(0, 6, "- none", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Access provisioning", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for a in access:
        pdf.cell(0, 6, f"- {a.access_type}: {a.status}", ln=True)
    if not access:
        pdf.cell(0, 6, "- none", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Checklist", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for it in items:
        pdf.cell(0, 6, f"- [{it.status}] {it.title_en}", ln=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Open items", ln=True)
    pdf.set_font("Helvetica", "", 10)
    for o in open_items:
        pdf.cell(0, 6, f"- {o.title} ({o.owner}, {o.status})", ln=True)
    if not open_items:
        pdf.cell(0, 6, "- none", ln=True)
    pdf.ln(6)

    pdf.cell(0, 8, "IT signature: ____________________   Date: __________", ln=True)
    pdf.cell(0, 8, "Employee signature: ______________   Date: __________", ln=True)
    return bytes(pdf.output())


@router.get("/cases/{case_id}/handover.pdf")
def handover_pdf(case_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    case = db.get(OnboardingCase, case_id)
    if not case:
        raise HTTPException(404, "not found")
    items = (
        db.execute(select(ChecklistItem).where(ChecklistItem.case_id == case_id).order_by(ChecklistItem.sort_order))
        .scalars()
        .all()
    )
    hardware = db.execute(select(HardwareAsset).where(HardwareAsset.case_id == case_id)).scalars().all()
    access = db.execute(select(AccessRequest).where(AccessRequest.case_id == case_id)).scalars().all()
    open_items = db.execute(select(OpenItem).where(OpenItem.case_id == case_id)).scalars().all()
    data = build_pdf(case, items, hardware, access, open_items)
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=handover-{case_id}.pdf"},
    )
