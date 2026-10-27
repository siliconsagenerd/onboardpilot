"""E2E smoke test covering core user flows via FastAPI TestClient against live routes."""

from __future__ import annotations


def test_public_demo_and_guides(client):
    r = client.get("/api/public/demo")
    assert r.status_code == 200
    data = r.json()
    assert data["case"]["employee_name"] == "Anna Beispiel"
    assert len(data["checklist"]) >= 5

    r = client.get("/api/public/guides")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_role_logins_and_me(client):
    for username, role in [("admin", "it_admin"), ("manager", "manager"), ("employee", "employee")]:
        r = client.post("/api/auth/login", json={"username": username, "password": f"{username.capitalize()}123!"})
        assert r.status_code == 200, f"Login failed for {username}"
        token = r.json()["access_token"]
        assert token
        assert r.json()["role"] == role

        r_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r_me.status_code == 200
        assert r_me.json()["role"] == role


def admin_token(client):
    return client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"}).json()["access_token"]


def test_admin_case_lifecycle(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}

    # 1. Create a case
    r = client.post(
        "/api/cases",
        headers=h,
        json={
            "employee_name": "E2E Test Starter",
            "employee_email": "e2e@example.com",
            "role_template": "developer",
            "department": "Engineering",
            "start_date": "2026-11-01",
        },
    )
    assert r.status_code == 200
    case_id = r.json()["id"]

    # 2. Check auto-seeded checklist items exist
    r_check = client.get(f"/api/cases/{case_id}/checklist", headers=h)
    assert r_check.status_code == 200
    items = r_check.json()
    assert len(items) >= 4

    # 3. Request and approve an access grant
    r_acc = client.post(
        "/api/access",
        headers=h,
        json={"case_id": case_id, "access_type": "github_repo", "requester": "Team Lead"},
    )
    assert r_acc.status_code == 200
    acc_id = r_acc.json()["id"]

    r_app = client.patch(f"/api/access/{acc_id}", json={"status": "approved"}, headers=h)
    assert r_app.status_code == 200
    assert r_app.json()["status"] == "approved"

    # 4. Provision hardware
    r_hw = client.post(
        "/api/hardware",
        headers=h,
        json={
            "case_id": case_id,
            "asset_type": "laptop",
            "brand_model": "ThinkPad T14",
            "serial_number": "SN-E2E-9999",
        },
    )
    assert r_hw.status_code == 200
    hw_id = r_hw.json()["id"]
    assert hw_id

    # 5. Handover PDF generates cleanly
    r_pdf = client.get(f"/api/cases/{case_id}/handover.pdf", headers=h)
    assert r_pdf.status_code == 200
    assert r_pdf.headers["content-type"] == "application/pdf"
    assert len(r_pdf.content) > 500

    # 6. Audit trail logged entries
    r_audit = client.get(f"/api/audit?case_id={case_id}", headers=h)
    assert r_audit.status_code == 200
    assert len(r_audit.json()) >= 1
