"""SQLAlchemy models for OnboardPilot."""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def new_id() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    email: Mapped[str] = mapped_column(String(200), unique=True)
    full_name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(30))  # it_admin / manager / employee
    password_hash: Mapped[str] = mapped_column(String(200))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now)


class OnboardingCase(Base):
    __tablename__ = "onboarding_cases"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    employee_name: Mapped[str] = mapped_column(String(200))
    employee_email: Mapped[str] = mapped_column(String(200), default="")
    role_template: Mapped[str] = mapped_column(String(40))  # developer / office_hr / sales / manager
    department: Mapped[str] = mapped_column(String(120), default="")
    start_date: Mapped[str] = mapped_column(String(10), default="")  # ISO date string
    manager_name: Mapped[str] = mapped_column(String(200), default="")
    manager_email: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[str] = mapped_column(String(40), default="pre_boarding")
    is_public_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str] = mapped_column(String(80), default="system")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now, onupdate=now)

    checklist_items: Mapped[list["ChecklistItem"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    hardware: Mapped[list["HardwareAsset"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    access_requests: Mapped[list["AccessRequest"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    open_items: Mapped[list["OpenItem"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    audit_entries: Mapped[list["AuditLog"]] = relationship(back_populates="case", cascade="all, delete-orphan")


class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("onboarding_cases.id", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(80), default="")
    title_de: Mapped[str] = mapped_column(String(300))
    title_en: Mapped[str] = mapped_column(String(300))
    description_de: Mapped[str] = mapped_column(Text, default="")
    description_en: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(40))  # Hardware/Account/Access/Software/Orientation/Documentation
    owner: Mapped[str] = mapped_column(String(30))  # it_admin / manager / employee
    status: Mapped[str] = mapped_column(String(30), default="not_started")  # not_started/in_progress/blocked/completed
    due_date: Mapped[str] = mapped_column(String(10), default="")
    depends_on: Mapped[list] = mapped_column(JSON, default=list)  # list of keys
    blocked_reason: Mapped[str] = mapped_column(Text, default="")
    completed_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_by: Mapped[str] = mapped_column(String(80), default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now)

    case: Mapped["OnboardingCase"] = relationship(back_populates="checklist_items")


class HardwareAsset(Base):
    __tablename__ = "hardware_assets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("onboarding_cases.id", ondelete="SET NULL"), nullable=True)
    asset_type: Mapped[str] = mapped_column(String(60))  # laptop/monitor/dock/headset/phone/accessory
    brand_model: Mapped[str] = mapped_column(String(200), default="")
    serial_number: Mapped[str] = mapped_column(String(200), default="")
    condition: Mapped[str] = mapped_column(String(40), default="new")  # new/good/used
    handover_date: Mapped[str] = mapped_column(String(10), default="")
    assigned_employee: Mapped[str] = mapped_column(String(200), default="")
    return_status: Mapped[str] = mapped_column(String(40), default="not_returned")  # not_returned/returned
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now)

    case: Mapped["OnboardingCase | None"] = relationship(back_populates="hardware")


class AccessRequest(Base):
    __tablename__ = "access_requests"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("onboarding_cases.id", ondelete="CASCADE"))
    access_type: Mapped[str] = mapped_column(String(60))  # email/vpn/m365_teams/shared_drive/git_tools/crm/hr_system
    status: Mapped[str] = mapped_column(String(30), default="requested")  # requested/approved/provisioned/verified
    requester: Mapped[str] = mapped_column(String(80), default="")
    approver: Mapped[str] = mapped_column(String(80), default="")
    provisioning_owner: Mapped[str] = mapped_column(String(80), default="")
    requested_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now)
    approved_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provisioned_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    case: Mapped["OnboardingCase"] = relationship(back_populates="access_requests")


class OpenItem(Base):
    __tablename__ = "open_items"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("onboarding_cases.id", ondelete="CASCADE"), nullable=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text, default="")
    owner: Mapped[str] = mapped_column(String(80), default="it_admin")
    due_date: Mapped[str] = mapped_column(String(10), default="")
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low/medium/high
    status: Mapped[str] = mapped_column(String(30), default="open")  # open/in_progress/blocked/resolved
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now)
    resolved_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    case: Mapped["OnboardingCase | None"] = relationship(back_populates="open_items")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    case_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("onboarding_cases.id", ondelete="CASCADE"), nullable=True)
    actor: Mapped[str] = mapped_column(String(80), default="system")
    action: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str] = mapped_column(String(60))
    entity_id: Mapped[str] = mapped_column(String(36), default="")
    description: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now)

    case: Mapped["OnboardingCase | None"] = relationship(back_populates="audit_entries")


class Guide(Base):
    __tablename__ = "guides"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    slug: Mapped[str] = mapped_column(String(80), unique=True)
    title_de: Mapped[str] = mapped_column(String(300))
    title_en: Mapped[str] = mapped_column(String(300))
    content_de: Mapped[str] = mapped_column(Text)
    content_en: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(60), default="general")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=now)
