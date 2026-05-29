"""Account and schema discovery tools.

Useful for verifying connectivity and for discovering which (custom) object
types exist in the connected HubSpot account.
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_get_account_details() -> dict[str, Any]:
        """Get details about the connected HubSpot account.

        Returns portal ID, time zone, currency, data-hosting region, and the
        UTC offset. Handy as a connectivity / auth check.
        """

        return await api(get_client, "GET", "/account-info/v3/details")

    @mcp.tool()
    async def hubspot_list_object_schemas() -> dict[str, Any]:
        """List all custom object schemas defined in the account.

        Use this to discover custom object types (names and ``objectTypeId``s)
        that can then be passed as ``object_type`` to the generic CRM tools.
        """

        return await api(get_client, "GET", "/crm-object-schemas/v3/schemas")

    @mcp.tool()
    async def hubspot_get_object_schema(object_type: str) -> dict[str, Any]:
        """Get the full schema for a single object type.

        Args:
            object_type: Object type name or ``objectTypeId`` (e.g. '2-12345678').
        """

        return await api(
            get_client, "GET", f"/crm-object-schemas/v3/schemas/{object_type}"
        )
