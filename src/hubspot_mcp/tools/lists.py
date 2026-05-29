"""CRM Lists tools.

Lists segment records (usually contacts) either statically (manual membership)
or dynamically (filter-based / "active"). Lists are central to targeting
marketing emails and campaigns.

Common ``object_type_id`` values: contacts = "0-1", companies = "0-2".
``processing_type``: "MANUAL" (static), "DYNAMIC" (filter-based), or "SNAPSHOT".
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_create_list(
        name: str,
        object_type_id: str = "0-1",
        processing_type: str = "MANUAL",
        filter_branch: dict[str, Any] | None = None,
        list_folder_id: int | None = None,
    ) -> dict[str, Any]:
        """Create a list.

        Args:
            name: List name.
            object_type_id: Object type the list contains (default "0-1" =
                contacts).
            processing_type: "MANUAL" (static), "DYNAMIC" (filter-based), or
                "SNAPSHOT".
            filter_branch: Required for DYNAMIC lists — the filter definition
                describing membership criteria.
            list_folder_id: Optional folder to create the list in.
        """

        body: dict[str, Any] = {
            "name": name,
            "objectTypeId": object_type_id,
            "processingType": processing_type,
        }
        if filter_branch is not None:
            body["filterBranch"] = filter_branch
        if list_folder_id is not None:
            body["listFolderId"] = list_folder_id
        return await api(get_client, "POST", "/crm/v3/lists", json=body)

    @mcp.tool()
    async def hubspot_get_list(
        list_id: str, include_filters: bool = False
    ) -> dict[str, Any]:
        """Get a list by ID.

        Args:
            list_id: The list's ILS list ID.
            include_filters: Include the list's filter definition.
        """

        return await api(
            get_client,
            "GET",
            f"/crm/v3/lists/{list_id}",
            params={"includeFilters": include_filters},
        )

    @mcp.tool()
    async def hubspot_search_lists(
        query: str | None = None,
        list_ids: list[str] | None = None,
        processing_types: list[str] | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search lists by name and/or attributes.

        Args:
            query: Text to match against list names.
            list_ids: Restrict to specific list IDs.
            processing_types: Filter by processing type(s).
            limit: Page size.
            offset: Result offset for pagination.
        """

        body: dict[str, Any] = {"count": limit, "offset": offset}
        if query is not None:
            body["query"] = query
        if list_ids is not None:
            body["listIds"] = list_ids
        if processing_types is not None:
            body["processingTypes"] = processing_types
        return await api(get_client, "POST", "/crm/v3/lists/search", json=body)

    @mcp.tool()
    async def hubspot_delete_list(list_id: str) -> dict[str, Any]:
        """Delete a list (the records themselves are not deleted).

        Args:
            list_id: The list's ID.
        """

        await api(get_client, "DELETE", f"/crm/v3/lists/{list_id}")
        return {"deleted": True, "listId": list_id}

    @mcp.tool()
    async def hubspot_get_list_memberships(
        list_id: str, limit: int = 100, after: str | None = None
    ) -> dict[str, Any]:
        """Get the record IDs that are members of a list.

        Args:
            list_id: The list's ID.
            limit: Page size.
            after: Pagination cursor.
        """

        return await api(
            get_client,
            "GET",
            f"/crm/v3/lists/{list_id}/memberships",
            params={"limit": limit, "after": after},
        )

    @mcp.tool()
    async def hubspot_add_list_members(
        list_id: str, record_ids: list[str]
    ) -> dict[str, Any]:
        """Add records to a MANUAL/static list.

        Args:
            list_id: The list's ID.
            record_ids: Record IDs to add as members.
        """

        return await api(
            get_client,
            "PUT",
            f"/crm/v3/lists/{list_id}/memberships/add",
            json=record_ids,
        )

    @mcp.tool()
    async def hubspot_remove_list_members(
        list_id: str, record_ids: list[str]
    ) -> dict[str, Any]:
        """Remove records from a MANUAL/static list.

        Args:
            list_id: The list's ID.
            record_ids: Record IDs to remove.
        """

        return await api(
            get_client,
            "PUT",
            f"/crm/v3/lists/{list_id}/memberships/remove",
            json=record_ids,
        )
