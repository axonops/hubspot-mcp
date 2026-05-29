import pytest

from hubspot_mcp.config import DEFAULT_API_BASE_URL, ConfigError, load_settings


def _clear(monkeypatch):
    for var in (
        "HUBSPOT_AUTH_MODE",
        "HUBSPOT_ACCESS_TOKEN",
        "HUBSPOT_CLIENT_ID",
        "HUBSPOT_CLIENT_SECRET",
        "HUBSPOT_SERVER_URL",
        "HUBSPOT_BASE_URL",
        "HUBSPOT_TIMEOUT",
        "HUBSPOT_SCOPES",
        "HUBSPOT_PORT",
    ):
        monkeypatch.delenv(var, raising=False)


def test_token_mode_requires_token(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("HUBSPOT_AUTH_MODE", "token")
    with pytest.raises(ConfigError):
        load_settings()


def test_token_mode_defaults(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("HUBSPOT_ACCESS_TOKEN", "pat-na1-abc")
    settings = load_settings()
    assert settings.auth_mode == "token"
    assert settings.access_token == "pat-na1-abc"
    assert settings.api_base_url == DEFAULT_API_BASE_URL
    assert settings.timeout == 30.0


def test_mode_inferred_oauth_when_client_id_present(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("HUBSPOT_CLIENT_ID", "cid")
    monkeypatch.setenv("HUBSPOT_CLIENT_SECRET", "secret")
    monkeypatch.setenv("HUBSPOT_SERVER_URL", "https://mcp.example.com/")
    settings = load_settings()
    assert settings.auth_mode == "oauth"
    assert settings.client_id == "cid"
    assert settings.server_url == "https://mcp.example.com"  # trailing slash trimmed
    assert "crm.objects.contacts.read" in settings.scopes


def test_oauth_mode_missing_fields(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("HUBSPOT_AUTH_MODE", "oauth")
    monkeypatch.setenv("HUBSPOT_CLIENT_ID", "cid")
    # missing secret + server url
    with pytest.raises(ConfigError):
        load_settings()


def test_oauth_custom_scopes(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("HUBSPOT_CLIENT_ID", "cid")
    monkeypatch.setenv("HUBSPOT_CLIENT_SECRET", "secret")
    monkeypatch.setenv("HUBSPOT_SERVER_URL", "https://mcp.example.com")
    monkeypatch.setenv("HUBSPOT_SCOPES", "oauth, content  crm.lists.read")
    settings = load_settings()
    assert settings.scopes == ["oauth", "content", "crm.lists.read"]


def test_bad_timeout(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("HUBSPOT_ACCESS_TOKEN", "tok")
    monkeypatch.setenv("HUBSPOT_TIMEOUT", "soon")
    with pytest.raises(ConfigError):
        load_settings()
