"""Tests for access-request state machine."""

def admin_token(client):
    return client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"}).json()["access_token"]


def test_access_transition_valid(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    cases = client.get("/api/cases", headers=h).json()
    tom = [c for c in cases if c["employee_name"] == "Tom Muster"][0]
    accs = client.get(f"/api/access?case_id={tom['id']}", headers=h).json()
    req_item = [a for a in accs if a["status"] == "requested"][0]
    r = client.patch(f"/api/access/{req_item['id']}", json={"status": "approved"}, headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "approved"
    # then provisioned
    r = client.patch(f"/api/access/{req_item['id']}", json={"status": "provisioned"}, headers=h)
    assert r.status_code == 200
    # then verified
    r = client.patch(f"/api/access/{req_item['id']}", json={"status": "verified"}, headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "verified"


def test_access_revert_rejected(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    cases = client.get("/api/cases", headers=h).json()
    tom = [c for c in cases if c["employee_name"] == "Tom Muster"][0]
    accs = client.get(f"/api/access?case_id={tom['id']}", headers=h).json()
    # pick a verified one if exists else approved
    a = [x for x in accs if x["status"] in ("approved", "provisioned", "verified")][0]
    r = client.patch(f"/api/access/{a['id']}", json={"status": "requested"}, headers=h)
    assert r.status_code == 400


def test_access_skip_rejected(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    cases = client.get("/api/cases", headers=h).json()
    tom = [c for c in cases if c["employee_name"] == "Tom Muster"][0]
    accs = client.get(f"/api/access?case_id={tom['id']}", headers=h).json()
    req_item = [a for a in accs if a["status"] == "requested"]
    if req_item:
        r = client.patch(f"/api/access/{req_item[0]['id']}", json={"status": "verified"}, headers=h)
        assert r.status_code == 400
