# supervaize_hello_world/tests/test_data_resource_e2e.py
"""E2E tests for the contacts DataResource via FastAPI TestClient.

These tests verify the full data resource lifecycle:
list → get → create → update → delete → import
All without a real network — TestClient exercises the actual route handlers.
"""

BASE = "/supervaizer/agents/hello-world-ai-agent/data/contacts"


def test_list_contacts_returns_two_seeded_contacts(client):
    """GET /data/contacts/ returns the two seeded contacts."""
    resp = client.get(f"{BASE}/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2
    emails = {c["email"] for c in data}
    assert "alice@example.com" in emails
    assert "bob@example.com" in emails


def test_get_contact_by_id(client):
    """GET /data/contacts/{id} returns the correct contact."""
    resp = client.get(f"{BASE}/c1")
    assert resp.status_code == 200
    contact = resp.json()
    assert contact["id"] == "c1"
    assert contact["first_name"] == "Alice"


def test_get_contact_not_found(client):
    """GET /data/contacts/{id} returns 404 for unknown ID."""
    resp = client.get(f"{BASE}/does-not-exist")
    assert resp.status_code == 404


def test_create_contact(client):
    """POST /data/contacts/ creates a new contact and returns it with an id."""
    payload = {"first_name": "Carol", "last_name": "White", "email": "carol@example.com"}
    resp = client.post(f"{BASE}/", json=payload)
    assert resp.status_code == 201
    created = resp.json()
    assert "id" in created
    assert created["first_name"] == "Carol"
    assert created["email"] == "carol@example.com"


def test_create_contact_appears_in_list(client):
    """Contact created via POST appears in subsequent GET list (total = 3)."""
    client.post(f"{BASE}/", json={"first_name": "Dave", "email": "dave@example.com"})
    resp = client.get(f"{BASE}/")
    contacts = resp.json()
    assert len(contacts) == 3  # 2 seeded + 1 created
    emails = {c["email"] for c in contacts}
    assert "dave@example.com" in emails


def test_update_contact(client):
    """PUT /data/contacts/{id} merges fields — unchanged fields are preserved."""
    resp = client.put(f"{BASE}/c1", json={"first_name": "Alicia", "city": "Lyon"})
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["first_name"] == "Alicia"
    assert updated["city"] == "Lyon"
    assert updated["id"] == "c1"  # id must not change
    assert updated["email"] == "alice@example.com"  # unchanged fields preserved


def test_update_contact_not_found(client):
    """PUT /data/contacts/{id} returns 404 for unknown ID."""
    resp = client.put(f"{BASE}/does-not-exist", json={"first_name": "Ghost"})
    assert resp.status_code == 404


def test_delete_contact(client):
    """DELETE /data/contacts/{id} removes the contact."""
    resp = client.delete(f"{BASE}/c2")
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True
    # Confirm it is gone
    assert client.get(f"{BASE}/c2").status_code == 404


def test_delete_contact_not_found(client):
    """DELETE /data/contacts/{id} returns 404 for unknown ID."""
    resp = client.delete(f"{BASE}/no-such-id")
    assert resp.status_code == 404


def test_bulk_import(client):
    """POST /data/contacts/import/ inserts multiple contacts."""
    records = [
        {"first_name": "Eve", "email": "eve@example.com"},
        {"first_name": "Frank", "email": "frank@example.com"},
    ]
    resp = client.post(f"{BASE}/import/", json=records)
    assert resp.status_code == 200
    result = resp.json()
    assert result["created"] == 2

    # Verify they appear in list (2 seeded + 2 imported = 4 total)
    list_resp = client.get(f"{BASE}/")
    all_contacts = list_resp.json()
    assert len(all_contacts) == 4
    emails = {c["email"] for c in all_contacts}
    assert "eve@example.com" in emails
    assert "frank@example.com" in emails


def test_unauthenticated_request_rejected():
    """Requests without API key are rejected."""
    from fastapi.testclient import TestClient
    from supervaizer_control import sv_server

    unauth = TestClient(sv_server.app)
    resp = unauth.get(f"{BASE}/")
    assert resp.status_code in (401, 403)


def test_agent_registration_info_includes_contacts_resource():
    """Agent.registration_info declares contacts in data_resources."""
    from supervaizer_control import simple_agent

    info = simple_agent.registration_info
    assert "data_resources" in info
    names = [r["name"] for r in info["data_resources"]]
    assert "contacts" in names

    contacts_info = next(r for r in info["data_resources"] if r["name"] == "contacts")
    assert contacts_info["importable"] is True
    assert contacts_info["read_only"] is False
    assert contacts_info["operations"]["create"] is True
    assert contacts_info["operations"]["import"] is True
