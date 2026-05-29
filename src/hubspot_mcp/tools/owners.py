"""CRM owner tools.

Owners are HubSpot users that records can be assigned to. Owner IDs are used by
the ``hubspot_owner_id`` property on records.
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_list_owners(
        email: str | None = None,
        limit: int = 100,
        after: str | None = None,
        archived: bool = False,
    ) -> dict[str, Any]:
        """List CRM owners (users records can be assigned to).

        Args:
            email: Filter to the owner with this email address.
            limit: Page size (default 100).
            after: Pagination cursor.
            archived: Return archived owners.
        """

        return await api(
            get_client,
            "GET",
            "/crm/v3/owners",
            params={"email": email, "limit": limit, "after": after, "archived": archived},
        )

    @mcp.tool()
    async def hubspot_get_owner(owner_id: str, id_property: str = "id") -> dict[str, Any]:
        """Get a single owner by ID.

        Args:
            owner_id: The owner's ID (or userId if id_property='userId').
            id_property: Which identifier ``owner_id`` is — 'id' (default) or
                'userId'.
        """

        return await api(
            get_client,
            "GET",
            f"/crm/v3/owners/{owner_id}",
            params={"idProperty": id_property},
        )
