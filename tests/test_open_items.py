"""Tests for open items and audit trail."""


def admin_token(client):
    return client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"}).json()["access_token"]


def test_open_item_create_and_resolve(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    cases = client.get("/api/cases", headers=h).json()
    cid = cases[0]["id"]
    r = client.post(
        "/api/open-items",
        json={"case_id": cid, "title": "Test item", "owner": "it_admin", "priority": "high"},
        headers=h,
    )
    assert r.status_code == 200
    oid = r.json()["id"]
    r = client.patch(f"/api/open-items/{oid}", json={"status": "resolved"}, headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "resolved"
    assert r.json()["resolved_at"] != ""
    client.delete(f"/api/open-items/{oid}", headers=h)


def test_audit_entries_created(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    before = client.get("/api/audit", headers=h).json()
    c = client.post(
        "/api/cases",
        json={"employee_name": "Audit Test", "role_template": "developer", "start_date": "2026-10-20"},
        headers=h,
    ).json()
    after = client.get("/api/audit", headers=h).json()
    assert len(after) > len(before)
    actions = [a["action"] for a in after]
    assert "case_created" in actions
    client.delete(f"/api/cases/{c['id']}", headers=h)


def test_audit_filter_by_case(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    cases = client.get("/api/cases", headers=h).json()
    cid = cases[0]["id"]
    r = client.get(f"/api/audit?case_id={cid}", headers=h)
    assert r.status_code == 200
    for a in r.json():
        assert a["case_id"] == cid
