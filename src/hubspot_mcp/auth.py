"""OAuth authentication for the HubSpot MCP server (oauth mode).

HubSpot's OAuth is a confidential-client authorization-code flow: it needs a
client id/secret, issues opaque (non-JWT) access tokens that expire after ~30
minutes, and does not support Dynamic Client Registration. MCP clients (e.g.
Claude) expect a DCR-capable OAuth 2.1 authorization server.

We bridge the two with FastMCP's :class:`OAuthProxy`: it presents a DCR-style
interface to the MCP client while using our pre-registered HubSpot app
credentials upstream. The proxy forwards HubSpot's access token back to the
client, which then presents it on every MCP request; :class:`HubSpotTokenVerifier`
validates that token against HubSpot.
"""

from __future__ import annotations

import time

import httpx
from fastmcp.server.auth import AccessToken, OAuthProxy, TokenVerifier

from .config import (
    HUBSPOT_AUTHORIZE_URL,
    HUBSPOT_TOKEN_INFO_URL,
    HUBSPOT_TOKEN_URL,
    Settings,
)


class HubSpotTokenVerifier(TokenVerifier):
    """Validate opaque HubSpot access tokens via the token-info endpoint.

    HubSpot exposes ``GET /oauth/v1/access-tokens/{token}`` which returns the
    token's metadata (hub id, app id, user, scopes, seconds-to-expiry) when the
    token is valid. Results are cached briefly to avoid a HubSpot round-trip on
    every MCP request.
    """

    def __init__(
        self,
        *,
        token_info_url: str = HUBSPOT_TOKEN_INFO_URL,
        timeout: float = 10.0,
        cache_ttl: float = 300.0,
        required_scopes: list[str] | None = None,
    ):
        super().__init__(required_scopes=required_scopes)
        self._token_info_url = token_info_url.rstrip("/")
        self._timeout = timeout
        self._cache_ttl = cache_ttl
        self._cache: dict[str, tuple[float, AccessToken]] = {}

    async def verify_token(self, token: str) -> AccessToken | None:
        now = time.time()
        cached = self._cache.get(token)
        if cached and cached[0] > now:
            return cached[1]

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.get(f"{self._token_info_url}/{token}")
        except httpx.RequestError:
            return None

        if resp.status_code != 200:
            return None

        data = resp.json()
        expires_in = int(data.get("expires_in", 0) or 0)
        expires_at = int(now) + expires_in if expires_in else None

        access = AccessToken(
            token=token,
            client_id=str(data.get("app_id") or data.get("hub_id") or "hubspot"),
            scopes=list(data.get("scopes", []) or []),
            expires_at=expires_at,
            claims={
                "hub_id": data.get("hub_id"),
                "hub_domain": data.get("hub_domain"),
                "app_id": data.get("app_id"),
                "user": data.get("user"),
                "user_id": data.get("user_id"),
                "token_type": data.get("token_type"),
            },
        )

        # Cache until shortly before expiry (and never longer than cache_ttl).
        ttl = self._cache_ttl
        if expires_at is not None:
            ttl = min(ttl, max(0.0, expires_at - now - 30))
        if ttl > 0:
            self._cache[token] = (now + ttl, access)
        return access


def build_oauth_proxy(settings: Settings) -> OAuthProxy:
    """Construct the HubSpot :class:`OAuthProxy` from settings (oauth mode)."""

    verifier = HubSpotTokenVerifier(required_scopes=None)
    # OAuth client/token state is kept in-memory (single-VM deployment). A
    # server restart simply prompts users to re-authenticate.
    return OAuthProxy(
        upstream_authorization_endpoint=HUBSPOT_AUTHORIZE_URL,
        upstream_token_endpoint=HUBSPOT_TOKEN_URL,
        upstream_client_id=settings.client_id,
        upstream_client_secret=settings.client_secret,
        token_verifier=verifier,
        base_url=settings.server_url,
        valid_scopes=settings.scopes,
        # HubSpot's classic OAuth app flow does not use PKCE upstream; the proxy
        # still enforces PKCE with the MCP client regardless of this setting.
        forward_pkce=settings.forward_pkce,
        # HubSpot expects the client secret in the token request body.
        token_endpoint_auth_method="client_secret_post",
        require_authorization_consent=settings.require_consent,
    )


def build_auth(settings: Settings) -> OAuthProxy | None:
    """Return the auth provider for the configured mode (None in token mode)."""

    if settings.auth_mode == "oauth":
        return build_oauth_proxy(settings)
    return None
