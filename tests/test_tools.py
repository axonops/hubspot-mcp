import json

import httpx
import pytest
import respx
from fastmcp import Client

BASE = "https://api.hubapi.com"


@pytest.fixture
def server():
    import hubspot_mcp.server as srv

    srv._client = None  # fresh client per test
    return srv


async def test_all_expected_tools_registered(server):
    names = {t.name for t in await server.mcp.list_tools()}
    expected = {
        "hubspot_list_objects",
        "hubspot_get_object",
        "hubspot_create_object",
        "hubspot_update_object",
        "hubspot_delete_object",
        "hubspot_search_objects",
        "hubspot_batch_read_objects",
        "hubspot_list_properties",
        "hubspot_get_property",
        "hubspot_create_property",
        "hubspot_list_associations",
        "hubspot_associate_default",
        "hubspot_associate_labeled",
        "hubspot_delete_association",
        "hubspot_list_association_labels",
        "hubspot_list_owners",
        "hubspot_get_owner",
        "hubspot_list_pipelines",
        "hubspot_get_pipeline",
        "hubspot_list_pipeline_stages",
        "hubspot_create_note",
        "hubspot_create_task",
        "hubspot_get_account_details",
        "hubspot_list_object_schemas",
        "hubspot_get_object_schema",
    }
    assert expected <= names


@respx.mock
async def test_search_objects_builds_post_body(server):
    route = respx.post(f"{BASE}/crm/v3/objects/contacts/search").mock(
        return_value=httpx.Response(200, json={"results": [{"id": "1"}], "total": 1})
    )
    async with Client(server.mcp) as client:
        await client.call_tool(
            "hubspot_search_objects",
            {
                "object_type": "contacts",
                "filter_groups": [
                    {"filters": [{"propertyName": "email", "operator": "EQ", "value": "a@b.com"}]}
                ],
                "properties": ["email"],
                "limit": 10,
            },
        )
    assert route.called
    body = json.loads(route.calls.last.request.content)
    assert body["limit"] == 10
    assert body["properties"] == ["email"]
    assert body["filterGroups"][0]["filters"][0]["value"] == "a@b.com"


@respx.mock
async def test_request_sends_bearer_from_static_token(server):
    route = respx.get(f"{BASE}/crm/v3/objects/contacts").mock(
        return_value=httpx.Response(200, json={"results": []})
    )
    async with Client(server.mcp) as client:
        await client.call_tool("hubspot_list_objects", {"object_type": "contacts"})
    assert route.calls.last.request.headers["Authorization"] == "Bearer tok"


@respx.mock
async def test_create_note_creates_and_associates(server):
    note = respx.post(f"{BASE}/crm/v3/objects/notes").mock(
        return_value=httpx.Response(201, json={"id": "555", "properties": {}})
    )
    assoc = respx.put(
        f"{BASE}/crm/v4/objects/notes/555/associations/default/contacts/99"
    ).mock(return_value=httpx.Response(200, json={}))

    async with Client(server.mcp) as client:
        await client.call_tool(
            "hubspot_create_note",
            {
                "body": "Called the customer",
                "associations": [{"to_object_type": "contacts", "to_object_id": "99"}],
            },
        )
    assert note.called and assoc.called
    sent = json.loads(note.calls.last.request.content)
    assert sent["properties"]["hs_note_body"] == "Called the customer"
    assert "hs_timestamp" in sent["properties"]


@respx.mock
async def test_delete_object_returns_confirmation(server):
    respx.delete(f"{BASE}/crm/v3/objects/deals/42").mock(
        return_value=httpx.Response(204)
    )
    async with Client(server.mcp) as client:
        result = await client.call_tool(
            "hubspot_delete_object", {"object_type": "deals", "object_id": "42"}
        )
    assert result.data == {"archived": True, "object_type": "deals", "id": "42"}
