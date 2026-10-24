"""Tests for hardware handover effects."""

def admin_token(client):
    return client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"}).json()["access_token"]


def test_hardware_create_marks_checklist(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    c = client.post("/api/cases", json={"employee_name": "HW Test", "role_template": "developer", "start_date": "2026-10-20"}, headers=h).json()
    cid = c["id"]
    r = client.post("/api/hardware", json={"case_id": cid, "asset_type": "laptop", "brand_model": "TP", "serial_number": "S1", "handover_date": "2026-10-20", "assigned_employee": "HW Test"}, headers=h)
    assert r.status_code == 200
    items = client.get(f"/api/cases/{cid}/checklist", headers=h).json()
    laptop = [i for i in items if i["key"] == "laptop"][0]
    assert laptop["status"] == "completed"
    client.delete(f"/api/cases/{cid}", headers=h)


def test_hardware_list_filter(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    cases = client.get("/api/cases", headers=h).json()
    cid = cases[0]["id"]
    r = client.get(f"/api/hardware?case_id={cid}", headers=h)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_handover_pdf(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    cases = client.get("/api/cases", headers=h).json()
    cid = cases[0]["id"]
    r = client.get(f"/api/cases/{cid}/handover.pdf", headers=h)
    assert r.status_code == 200
    assert r.content[:4] == b"%PDF"
