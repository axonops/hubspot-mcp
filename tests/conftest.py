"""Shared test configuration.

Set token-mode env vars *before* anything imports ``hubspot_mcp.server`` (which
loads settings at import time), so the server imports cleanly with no auth
provider and a static test token. Individual tests still override the env as
needed via monkeypatch.
"""

import os

os.environ.setdefault("HUBSPOT_AUTH_MODE", "token")
os.environ.setdefault("HUBSPOT_ACCESS_TOKEN", "tok")
os.environ.setdefault("HUBSPOT_BASE_URL", "https://api.hubapi.com")
