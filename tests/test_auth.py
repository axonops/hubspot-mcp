import httpx
import respx
from fastmcp.server.auth import OAuthProxy

from hubspot_mcp.auth import HubSpotTokenVerifier, build_auth
from hubspot_mcp.config import Settings

BASE = "https://api.hubapi.com"
TOKEN_INFO = f"{BASE}/oauth/v1/access-tokens"


@respx.mock
async def test_verifier_accepts_valid_token():
    respx.get(f"{TOKEN_INFO}/good-token").mock(
        return_value=httpx.Response(
            200,
            json={
                "token": "good-token",
                "hub_id": 12345,
                "app_id": 67890,
                "user": "ada@example.com",
                "scopes": ["oauth", "crm.objects.contacts.read"],
                "expires_in": 1800,
            },
        )
    )
    verifier = HubSpotTokenVerifier()
    access = await verifier.verify_token("good-token")
    assert access is not None
    assert access.token == "good-token"
    assert "crm.objects.contacts.read" in access.scopes
    assert access.claims["hub_id"] == 12345
    assert access.expires_at is not None


@respx.mock
async def test_verifier_rejects_invalid_token():
    respx.get(f"{TOKEN_INFO}/bad-token").mock(
        return_value=httpx.Response(404, json={"message": "token not found"})
    )
    verifier = HubSpotTokenVerifier()
    assert await verifier.verify_token("bad-token") is None


@respx.mock
async def test_verifier_caches_result():
    route = respx.get(f"{TOKEN_INFO}/cached").mock(
        return_value=httpx.Response(
            200, json={"token": "cached", "hub_id": 1, "scopes": [], "expires_in": 1800}
        )
    )
    verifier = HubSpotTokenVerifier()
    await verifier.verify_token("cached")
    await verifier.verify_token("cached")
    assert route.call_count == 1  # second lookup served from cache


def test_build_auth_token_mode_returns_none():
    settings = Settings(auth_mode="token", access_token="tok")
    assert build_auth(settings) is None


def test_build_auth_oauth_mode_builds_proxy():
    settings = Settings(
        auth_mode="oauth",
        client_id="cid",
        client_secret="secret",
        server_url="https://mcp.example.com",
    )
    auth = build_auth(settings)
    assert isinstance(auth, OAuthProxy)
