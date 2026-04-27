# supervaize_hello_world/agent_data_resource.py
"""In-memory contacts data store and DataResource declaration for Hello World.

Demonstrates how an agent declares a DataResource so Studio can render
a generic CRUD table without any agent-specific UI code.

The in-memory store is intentionally simple — it resets on server restart.
Real agents would use a database repository instead of the dict below.
"""
import uuid
from typing import Any

from supervaizer import DataResource, DataResourceField, Editable, FieldType

# ---------------------------------------------------------------------------
# In-memory store (resets on restart — for demo purposes only)
# ---------------------------------------------------------------------------

_contacts: dict[str, dict[str, Any]] = {
    "c1": {"id": "c1", "first_name": "Alice", "last_name": "Smith", "email": "alice@example.com", "city": "Paris"},
    "c2": {"id": "c2", "first_name": "Bob", "last_name": "Jones", "email": "bob@example.com", "city": "London"},
}


def _list_contacts() -> list[dict[str, Any]]:
    return list(_contacts.values())


def _get_contact(contact_id: str) -> dict[str, Any] | None:
    return _contacts.get(contact_id)


def _create_contact(data: dict[str, Any]) -> dict[str, Any]:
    contact_id = str(uuid.uuid4())[:8]
    # Always generate a server-side id; ignore any id supplied in the payload.
    contact = {k: v for k, v in data.items() if k != "id"}
    contact["id"] = contact_id
    _contacts[contact_id] = contact
    return contact


def _update_contact(contact_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    if contact_id not in _contacts:
        return None
    _contacts[contact_id] = {**_contacts[contact_id], **data, "id": contact_id}
    return _contacts[contact_id]


def _delete_contact(contact_id: str) -> bool:
    if contact_id not in _contacts:
        return False
    del _contacts[contact_id]
    return True


def _import_contacts(records: list[dict[str, Any]]) -> dict[str, Any]:
    for record in records:
        contact_id = str(uuid.uuid4())[:8]
        _contacts[contact_id] = {**record, "id": contact_id}
    return {"created": len(records), "total": len(_contacts)}


# ---------------------------------------------------------------------------
# DataResource declaration
# ---------------------------------------------------------------------------

contacts_resource = DataResource(
    name="contacts",
    display_name="Contacts",
    description="Example in-memory contact list — resets on server restart",
    read_only=False,
    importable=True,
    fields=[
        DataResourceField(
            name="id",
            field_type=FieldType.STRING,
            label="ID",
            editable=Editable.NEVER,
            visible_on=["list", "detail"],
        ),
        DataResourceField(name="first_name", field_type=FieldType.STRING, label="First Name", required=True),
        DataResourceField(name="last_name", field_type=FieldType.STRING, label="Last Name"),
        DataResourceField(name="email", field_type=FieldType.EMAIL, label="Email", sensitive=True),
        DataResourceField(name="city", field_type=FieldType.STRING, label="City"),
    ],
    on_list=_list_contacts,
    on_get=_get_contact,
    on_create=_create_contact,
    on_update=_update_contact,
    on_delete=_delete_contact,
    on_import=_import_contacts,
)
