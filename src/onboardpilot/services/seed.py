"""Seed data for OnboardPilot."""

from __future__ import annotations

import datetime as dt
import os

from onboardpilot.auth import hash_password
from onboardpilot.db import SessionLocal
from onboardpilot.db.models import (
    AccessRequest,
    AuditLog,
    ChecklistItem,
    Guide,
    HardwareAsset,
    OnboardingCase,
    OpenItem,
    User,
)
from onboardpilot.services.templates import generate_checklist_items

GUIDES = [
    (
        "wifi",
        "Mit dem Firmen-WLAN verbinden",
        "Connect to company Wi-Fi",
        "1. WLAN-Einstellungen öffnen.\n2. Netzwerk 'Firma-Gast' wählen.\n3. Passwort eingeben.\n4. Verbindung bestätigen.",  # noqa: E501
        "1. Open Wi-Fi settings.\n2. Select 'Company-Guest' network.\n3. Enter password.\n4. Confirm connection.",
        "network",
    ),
    (
        "email",
        "E-Mail / Microsoft 365 einrichten",
        "Set up email / Microsoft 365",
        "1. Outlook öffnen.\n2. Konto hinzufügen.\n3. E-Mail und Passwort eingeben.\n4. Anmeldung abschließen.",
        "1. Open Outlook.\n2. Add account.\n3. Enter email and password.\n4. Complete sign-in.",
        "email",
    ),
    (
        "vpn",
        "VPN verwenden",
        "Use the VPN",
        "1. VPN-Client starten.\n2. Server wählen.\n3. Mit Zugangsdaten anmelden.\n4. Verbindung prüfen.",
        "1. Start VPN client.\n2. Select server.\n3. Sign in with credentials.\n4. Verify connection.",
        "network",
    ),
    (
        "password",
        "Passwort zurücksetzen",
        "Reset your password",
        "1. Anmeldeseite öffnen.\n2. 'Passwort vergessen' wählen.\n3. E-Mail eingeben.\n4. Link folgen.",
        "1. Open login page.\n2. Choose 'Forgot password'.\n3. Enter email.\n4. Follow the link.",
        "account",
    ),
    (
        "teams",
        "Teams einrichten",
        "Set up Teams",
        "1. Teams installieren.\n2. Mit Firmenkonto anmelden.\n3. Benachrichtigungen prüfen.",
        "1. Install Teams.\n2. Sign in with company account.\n3. Check notifications.",
        "communication",
    ),
    (
        "printer",
        "Drucker verbinden",
        "Connect a printer",
        "1. Drucker suchen.\n2. Treiber installieren.\n3. Testseite drucken.",
        "1. Find printer.\n2. Install driver.\n3. Print test page.",
        "hardware",
    ),
    (
        "software",
        "Software anfordern",
        "Request software",
        "1. IT-Portal öffnen.\n2. Software auswählen.\n3. Antrag senden.\n4. Auf Freigabe warten.",
        "1. Open IT portal.\n2. Select software.\n3. Submit request.\n4. Wait for approval.",
        "software",
    ),
    (
        "issue",
        "IT-Problem melden",
        "Report an IT issue",
        "1. Ticket erstellen.\n2. Problem beschreiben.\n3. Priorität wählen.\n4. Absenden.",
        "1. Create ticket.\n2. Describe issue.\n3. Choose priority.\n4. Submit.",
        "support",
    ),
]


def seed_if_empty() -> None:
    db = SessionLocal()
    try:
        if db.query(OnboardingCase).count() > 0:
            # ensure users exist
            _seed_users(db)
            db.commit()
            return
        _seed_users(db)
        _seed_guides(db)
        _seed_cases(db)
        db.commit()
    finally:
        db.close()


def _seed_users(db) -> None:
    if db.query(User).count() > 0:
        return
    users = [
        (
            "admin",
            "it.admin@onboardpilot.demo",
            "IT Administrator",
            "it_admin",
            os.getenv("SEED_ADMIN_PASSWORD", "Admin123!"),
        ),
        (
            "manager",
            "manager@onboardpilot.demo",
            "Team Manager",
            "manager",
            os.getenv("SEED_MANAGER_PASSWORD", "Manager123!"),
        ),
        (
            "employee",
            "employee@onboardpilot.demo",
            "New Employee",
            "employee",
            os.getenv("SEED_EMPLOYEE_PASSWORD", "Employee123!"),
        ),
    ]
    for u, e, name, role, pw in users:
        db.add(User(username=u, email=e, full_name=name, role=role, password_hash=hash_password(pw)))


def _seed_guides(db) -> None:
    existing = {g.slug for g in db.query(Guide).all()}
    for slug, td, te, cd, ce, cat in GUIDES:
        if slug in existing:
            continue
        db.add(Guide(slug=slug, title_de=td, title_en=te, content_de=cd, content_en=ce, category=cat))


def _seed_cases(db) -> None:
    today = dt.date.today()
    monday = today + dt.timedelta(days=(7 - today.weekday()) % 7)
    if monday == today:
        monday = today + dt.timedelta(days=7)

    # 1. Public demo completed case: Anna Beispiel, Developer
    c1 = OnboardingCase(
        employee_name="Anna Beispiel",
        employee_email="anna.beispiel@demo.local",
        role_template="developer",
        department="Engineering",
        start_date=(today - dt.timedelta(days=14)).isoformat(),
        manager_name="David Beispiel",
        manager_email="david.beispiel@demo.local",
        status="completed",
        is_public_demo=True,
        created_by="seed",
    )
    db.add(c1)
    db.flush()
    items = generate_checklist_items(c1.id, "developer", c1.start_date)
    for it in items:
        ci = ChecklistItem(**it)
        ci.status = "completed"
        ci.completed_by = "seed"
        ci.completed_at = dt.datetime.now(dt.UTC)
        db.add(ci)
    # hardware
    for at, bm, sn in [
        ("laptop", "ThinkPad T14", "SN-ANNA-001"),
        ("monitor", 'Dell 24"', "SN-ANNA-002"),
        ("dock", "USB-C Dock", "SN-ANNA-003"),
    ]:
        db.add(
            HardwareAsset(
                case_id=c1.id,
                asset_type=at,
                brand_model=bm,
                serial_number=sn,
                condition="new",
                handover_date=c1.start_date,
                assigned_employee="Anna Beispiel",
                return_status="not_returned",
            )
        )
    # access requests all verified/provisioned
    for at in ["email", "vpn", "m365_teams", "git_tools"]:
        st = "verified" if at in ("email", "vpn", "m365_teams", "git_tools") else "provisioned"
        ar = AccessRequest(
            case_id=c1.id,
            access_type=at,
            status=st,
            requester="seed",
            approver="admin",
            provisioning_owner="admin",
            notes="Demo",
        )
        ar.requested_at = dt.datetime.now(dt.UTC)
        ar.approved_at = dt.datetime.now(dt.UTC)
        ar.provisioned_at = dt.datetime.now(dt.UTC)
        ar.verified_at = dt.datetime.now(dt.UTC)
        db.add(ar)
    # one open item
    db.add(
        OpenItem(
            case_id=c1.id,
            title="Monitor stand pending delivery",
            description="Monitor stand not yet delivered",
            owner="it_admin",
            due_date=(today + dt.timedelta(days=3)).isoformat(),
            priority="low",
            status="open",
        )
    )
    db.add(
        AuditLog(
            case_id=c1.id,
            actor="seed",
            action="case_created",
            entity_type="case",
            entity_id=c1.id,
            description="Created onboarding case for Anna Beispiel",
        )
    )
    db.add(
        AuditLog(
            case_id=c1.id,
            actor="admin",
            action="item_completed",
            entity_type="checklist",
            entity_id=c1.id,
            description="Completed onboarding checklist",
        )
    )

    # 2. In-progress case with blocked access
    c2 = OnboardingCase(
        employee_name="Tom Muster",
        employee_email="tom.muster@demo.local",
        role_template="office_hr",
        department="Human Resources",
        start_date=(today - dt.timedelta(days=3)).isoformat(),
        manager_name="Maria Beispiel",
        manager_email="maria.beispiel@demo.local",
        status="accounts_provisioned",
        created_by="seed",
    )
    db.add(c2)
    db.flush()
    items2 = generate_checklist_items(c2.id, "office_hr", c2.start_date)
    for it in items2:
        ci = ChecklistItem(**it)
        if it["key"] in ("laptop", "email"):
            ci.status = "completed"
            ci.completed_by = "seed"
            ci.completed_at = dt.datetime.now(dt.UTC)
        db.add(ci)
    db.add(
        HardwareAsset(
            case_id=c2.id,
            asset_type="laptop",
            brand_model="Latitude 5540",
            serial_number="SN-TOM-001",
            condition="new",
            handover_date=c2.start_date,
            assigned_employee="Tom Muster",
        )
    )
    # access: email verified, m365 requested (blocked-ish), shared_drive requested
    for at, st in [
        ("email", "verified"),
        ("m365_teams", "requested"),
        ("shared_drive", "requested"),
        ("hr_system", "approved"),
    ]:
        ar = AccessRequest(
            case_id=c2.id, access_type=at, status=st, requester="seed", approver="admin", provisioning_owner="admin"
        )
        ar.requested_at = dt.datetime.now(dt.UTC)
        if st in ("approved", "provisioned", "verified"):
            ar.approved_at = dt.datetime.now(dt.UTC)
        if st in ("provisioned", "verified"):
            ar.provisioned_at = dt.datetime.now(dt.UTC)
        if st == "verified":
            ar.verified_at = dt.datetime.now(dt.UTC)
        db.add(ar)
    db.add(
        OpenItem(
            case_id=c2.id,
            title="VPN client installation pending",
            description="Employee needs help installing VPN",
            owner="it_admin",
            due_date=(today + dt.timedelta(days=1)).isoformat(),
            priority="high",
            status="open",
        )
    )
    db.add(
        AuditLog(
            case_id=c2.id,
            actor="seed",
            action="case_created",
            entity_type="case",
            entity_id=c2.id,
            description="Created onboarding case for Tom Muster",
        )
    )

    # 3. Upcoming Monday starter
    c3 = OnboardingCase(
        employee_name="Maria Beispiel",
        employee_email="maria.beispiel@demo.local",
        role_template="manager",
        department="Operations",
        start_date=monday.isoformat(),
        manager_name="David Beispiel",
        manager_email="david.beispiel@demo.local",
        status="pre_boarding",
        created_by="seed",
    )
    db.add(c3)
    db.flush()
    for it in generate_checklist_items(c3.id, "manager", c3.start_date):
        db.add(ChecklistItem(**it))
    db.add(
        HardwareAsset(
            case_id=c3.id,
            asset_type="laptop",
            brand_model="MacBook Pro 14",
            serial_number="SN-MARIA-001",
            condition="new",
            assigned_employee="Maria Beispiel",
        )
    )
    db.add(
        AuditLog(
            case_id=c3.id,
            actor="seed",
            action="case_created",
            entity_type="case",
            entity_id=c3.id,
            description="Created onboarding case for Maria Beispiel",
        )
    )

    # 4. Sales case in progress
    c4 = OnboardingCase(
        employee_name="David Beispiel",
        employee_email="david.beispiel@demo.local",
        role_template="sales",
        department="Sales",
        start_date=(today - dt.timedelta(days=7)).isoformat(),
        manager_name="Maria Beispiel",
        manager_email="maria.beispiel@demo.local",
        status="first_week_support",
        created_by="seed",
    )
    db.add(c4)
    db.flush()
    for it in generate_checklist_items(c4.id, "sales", c4.start_date):
        ci = ChecklistItem(**it)
        if it["key"] in ("laptop", "email", "m365", "headset"):
            ci.status = "completed"
            ci.completed_by = "seed"
            ci.completed_at = dt.datetime.now(dt.UTC)
        db.add(ci)
    db.add(
        HardwareAsset(
            case_id=c4.id,
            asset_type="laptop",
            brand_model="ThinkPad X1",
            serial_number="SN-DAVID-001",
            condition="good",
            handover_date=c4.start_date,
            assigned_employee="David Beispiel",
        )
    )
    db.add(
        HardwareAsset(
            case_id=c4.id,
            asset_type="headset",
            brand_model="Jabra Evolve",
            serial_number="SN-DAVID-002",
            condition="new",
            handover_date=c4.start_date,
            assigned_employee="David Beispiel",
        )
    )
    db.add(
        HardwareAsset(
            case_id=c4.id,
            asset_type="monitor",
            brand_model='Dell 24"',
            serial_number="SN-DAVID-003",
            condition="new",
            assigned_employee="",
        )
    )
    for at, st in [("email", "verified"), ("crm", "provisioned"), ("shared_drive", "approved")]:
        ar = AccessRequest(
            case_id=c4.id, access_type=at, status=st, requester="seed", approver="admin", provisioning_owner="admin"
        )
        ar.requested_at = dt.datetime.now(dt.UTC)
        if st in ("approved", "provisioned", "verified"):
            ar.approved_at = dt.datetime.now(dt.UTC)
        if st in ("provisioned", "verified"):
            ar.provisioned_at = dt.datetime.now(dt.UTC)
        if st == "verified":
            ar.verified_at = dt.datetime.now(dt.UTC)
        db.add(ar)
    db.add(
        OpenItem(
            case_id=c4.id,
            title="CRM training session",
            description="Schedule CRM onboarding training",
            owner="manager",
            due_date=(today + dt.timedelta(days=5)).isoformat(),
            priority="medium",
            status="open",
        )
    )
    db.add(
        AuditLog(
            case_id=c4.id,
            actor="seed",
            action="case_created",
            entity_type="case",
            entity_id=c4.id,
            description="Created onboarding case for David Beispiel",
        )
    )

    # Bulk demo cases (50 total mix)
    _seed_bulk_cases(db, today, monday)


def _seed_bulk_cases(db, today, monday):
    import random

    random.seed(42)
    first_names = [
        "Lukas",
        "Sophie",
        "Maximilian",
        "Laura",
        "Felix",
        "Hannah",
        "Leon",
        "Mia",
        "Paul",
        "Emma",
        "Jonas",
        "Lena",
        "Tim",
        "Anna",
        "Niklas",
        "Sarah",
        "Moritz",
        "Julia",
        "David",
        "Marie",
        "Tobias",
        "Lisa",
        "Jan",
        "Katharina",
        "Florian",
        "Nina",
        "Sebastian",
        "Clara",
        "Markus",
        "Franziska",
    ]
    last_names = [
        "Müller",
        "Schmidt",
        "Schneider",
        "Fischer",
        "Weber",
        "Meyer",
        "Wagner",
        "Becker",
        "Schulz",
        "Hoffmann",
        "Schäfer",
        "Koch",
        "Bauer",
        "Richter",
        "Klein",
        "Wolf",
        "Schröder",
        "Neumann",
        "Schwarz",
        "Zimmermann",
        "Braun",
        "Krüger",
        "Hofmann",
        "Hartmann",
        "Lange",
        "Schmitt",
        "Werner",
        "Krause",
        "Meier",
        "Lehmann",
    ]
    roles = ["developer", "office_hr", "sales", "manager"]
    depts = {"developer": "Engineering", "office_hr": "Human Resources", "sales": "Sales", "manager": "Operations"}
    statuses = [
        "pre_boarding",
        "hardware_ready",
        "accounts_provisioned",
        "orientation_complete",
        "first_week_support",
        "completed",
    ]
    access_types = ["email", "vpn", "m365_teams", "git_tools", "crm", "shared_drive", "hr_system"]
    hardware_items = [("laptop", "ThinkPad X1", "SN"), ("monitor", 'Dell 24"', "SN"), ("headset", "Jabra Evolve", "SN")]
    for i in range(46):
        fn = first_names[i % len(first_names)]
        ln = last_names[i % len(last_names)]
        name = f"{fn} {ln}"
        role = roles[i % len(roles)]
        dept = depts[role]
        # spread start dates: some past, some upcoming
        days_offset = (i % 7) - 3  # -3..3
        if i % 5 == 0:
            start = monday + dt.timedelta(days=(i % 4) + 1)
        else:
            start = today + dt.timedelta(days=days_offset)
        status = statuses[i % len(statuses)]
        # completed cases get more completed items
        c = OnboardingCase(
            employee_name=name,
            employee_email=f"{fn.lower()}.{ln.lower()}@demo.local",
            role_template=role,
            department=dept,
            start_date=start.isoformat(),
            manager_name="David Beispiel",
            manager_email="david.beispiel@demo.local",
            status=status,
            created_by="seed",
        )
        db.add(c)
        db.flush()
        items = generate_checklist_items(c.id, role, c.start_date)
        for it in items:
            ci = ChecklistItem(**it)
            if status in ("completed", "first_week_support", "orientation_complete"):
                if it["sort_order"] <= len(items) * 0.7:
                    ci.status = "completed"
                    ci.completed_by = "seed"
                    ci.completed_at = dt.datetime.now(dt.UTC)
            elif status in ("accounts_provisioned", "hardware_ready"):
                if it["sort_order"] <= len(items) * 0.4:
                    ci.status = "completed"
                    ci.completed_by = "seed"
                    ci.completed_at = dt.datetime.now(dt.UTC)
            db.add(ci)
        # hardware: 1-2 items, some handed over
        for j, (at, bm, prefix) in enumerate(hardware_items[: (i % 2) + 1]):
            handover = c.start_date if (j == 0 and status not in ("pre_boarding",)) else None
            db.add(
                HardwareAsset(
                    case_id=c.id,
                    asset_type=at,
                    brand_model=bm,
                    serial_number=f"{prefix}-{name.split()[1].upper()[:4]}-{j + 1:03d}",
                    condition="new",
                    handover_date=handover,
                    assigned_employee=name if handover else "",
                )
            )
        # access requests: 2-3, varied statuses
        for at in access_types[: (i % 3) + 2]:
            st = "requested"
            if status in ("completed", "first_week_support"):
                st = "verified" if at in ("email", "vpn") else "provisioned"
            elif status in ("accounts_provisioned", "orientation_complete"):
                st = "approved" if at in ("email",) else "requested"
            elif status == "hardware_ready":
                st = "requested"
            ar = AccessRequest(
                case_id=c.id, access_type=at, status=st, requester="seed", approver="admin", provisioning_owner="admin"
            )
            ar.requested_at = dt.datetime.now(dt.UTC)
            if st in ("approved", "provisioned", "verified"):
                ar.approved_at = dt.datetime.now(dt.UTC)
            if st in ("provisioned", "verified"):
                ar.provisioned_at = dt.datetime.now(dt.UTC)
            if st == "verified":
                ar.verified_at = dt.datetime.now(dt.UTC)
            db.add(ar)
        # open item for some
        if i % 3 == 0:
            db.add(
                OpenItem(
                    case_id=c.id,
                    title="Follow-up task",
                    description="Pending follow-up",
                    owner="it_admin",
                    due_date=(today + dt.timedelta(days=3)).isoformat(),
                    priority="medium",
                    status="open",
                )
            )
        db.add(
            AuditLog(
                case_id=c.id,
                actor="seed",
                action="case_created",
                entity_type="case",
                entity_id=c.id,
                description=f"Created onboarding case for {name}",
            )
        )


if __name__ == "__main__":
    seed_if_empty()
    print("seed complete")
