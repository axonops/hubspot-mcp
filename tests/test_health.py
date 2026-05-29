"""Kubernetes health-probe endpoints.

These are plain unauthenticated HTTP routes on the FastMCP app, exercised here
against the ASGI app (no running server / no network).
"""

import httpx
import pytest


@pytest.fixture
def app():
    import hubspot_mcp.server as srv

    srv._client = None
    return srv.mcp.http_app()


async def _get(app, path):
    transport = httpx.ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get(path)


async def test_healthz_ok_without_auth(app):
    resp = await _get(app, "/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "hubspot-mcp"


async def test_readyz_ok_without_auth(app):
    resp = await _get(app, "/readyz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"
