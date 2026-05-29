"""Console entry point for the HubSpot MCP server.

* ``oauth`` mode runs over HTTP (Streamable HTTP) so MCP clients can perform the
  browser-based OAuth handshake and connect remotely.
* ``token`` mode runs over stdio, which is what local MCP clients expect when
  launching the server as a subprocess.
"""

from __future__ import annotations

import sys

from .config import ConfigError


def main() -> None:
    # Import (and thus configuration loading) happens here so misconfiguration
    # fails fast with a clear message rather than on the first tool call.
    try:
        from .server import mcp, settings
    except ConfigError as exc:
        print(f"hubspot-mcp: configuration error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    if settings.auth_mode == "oauth":
        print(
            f"hubspot-mcp: serving over HTTP on {settings.host}:{settings.port} "
            f"(public URL {settings.server_url}); OAuth proxy in front of HubSpot.",
            file=sys.stderr,
        )
        mcp.run(transport="http", host=settings.host, port=settings.port)
    else:
        mcp.run()  # stdio


if __name__ == "__main__":
    main()
