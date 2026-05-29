import json

import httpx
import pytest
import respx
from fastmcp import Client

BASE = "https://api.hubapi.com"


@pytest.fixture
def server():
    import hubspot_mcp.server as srv

    srv._client = None
    return srv


async def test_marketing_tools_registered(server):
    names = {t.name for t in await server.mcp.list_tools()}
    expected = {
        "hubspot_list_campaigns",
        "hubspot_create_campaign",
        "hubspot_get_campaign_metrics",
        "hubspot_create_marketing_email",
        "hubspot_publish_marketing_email",
        "hubspot_send_transactional_email",
        "hubspot_send_marketing_email",
        "hubspot_create_form",
        "hubspot_create_list",
        "hubspot_add_list_members",
        "hubspot_subscribe",
        "hubspot_list_marketing_events",
        "hubspot_list_flows",
    }
    assert expected <= names


@respx.mock
async def test_send_transactional_email_builds_body(server):
    route = respx.post(f"{BASE}/marketing/v3/transactional/single-email/send").mock(
        return_value=httpx.Response(200, json={"requestedAt": "now", "statusId": "abc"})
    )
    async with Client(server.mcp) as client:
        await client.call_tool(
            "hubspot_send_transactional_email",
            {
                "email_id": 12345,
                "to": "ada@example.com",
                "contact_properties": {"firstname": "Ada"},
                "custom_properties": {"order_id": "X-1"},
            },
        )
    body = json.loads(route.calls.last.request.content)
    assert body["emailId"] == 12345
    assert body["message"]["to"] == "ada@example.com"
    assert body["contactProperties"]["firstname"] == "Ada"
    assert body["customProperties"]["order_id"] == "X-1"


@respx.mock
async def test_create_campaign_wraps_properties(server):
    route = respx.post(f"{BASE}/marketing/v3/campaigns").mock(
        return_value=httpx.Response(201, json={"id": "guid-1", "properties": {}})
    )
    async with Client(server.mcp) as client:
        await client.call_tool(
            "hubspot_create_campaign", {"properties": {"hs_name": "Spring Launch"}}
        )
    body = json.loads(route.calls.last.request.content)
    assert body == {"properties": {"hs_name": "Spring Launch"}}


@respx.mock
async def test_add_list_members_sends_id_array(server):
    route = respx.put(f"{BASE}/crm/v3/lists/99/memberships/add").mock(
        return_value=httpx.Response(200, json={"recordsIdsAdded": ["1", "2"]})
    )
    async with Client(server.mcp) as client:
        await client.call_tool(
            "hubspot_add_list_members", {"list_id": "99", "record_ids": ["1", "2"]}
        )
    body = json.loads(route.calls.last.request.content)
    assert body == ["1", "2"]


@respx.mock
async def test_publish_marketing_email(server):
    route = respx.post(f"{BASE}/marketing/v3/emails/77/publish").mock(
        return_value=httpx.Response(200, json={"id": "77", "state": "PUBLISHED"})
    )
    async with Client(server.mcp) as client:
        await client.call_tool("hubspot_publish_marketing_email", {"email_id": "77"})
    assert route.called
