"""Generic CRM object tools.

A single set of tools works across every standard and custom CRM object by
taking an ``object_type`` argument. Common object types:

    contacts, companies, deals, tickets, line_items, products, quotes,
    notes, tasks, emails, calls, meetings

Custom objects may be referenced by their fully-qualified name or object type
ID (e.g. ``2-12345678``).
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api

_OBJECT_TYPE_NOTE = (
    "CRM object type, e.g. 'contacts', 'companies', 'deals', 'tickets', "
    "'line_items', 'products', 'quotes', 'notes', 'tasks', 'emails', "
    "'calls', 'meetings', or a custom object name / type id like '2-12345678'."
)


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_list_objects(
        object_type: str,
        limit: int = 50,
        after: str | None = None,
        properties: list[str] | None = None,
        associations: list[str] | None = None,
        archived: bool = False,
    ) -> dict[str, Any]:
        """List CRM records of a given type (paginated).

        Args:
            object_type: %s
            limit: Page size, 1-100 (default 50).
            after: Pagination cursor from a previous response's
                ``paging.next.after``.
            properties: Property names to return. If omitted HubSpot returns a
                small default set.
            associations: Other object types to return associated record IDs
                for (e.g. ["companies", "deals"]).
            archived: Return archived (deleted) records instead of active ones.

        Returns:
            HubSpot collection response with ``results`` and ``paging``.
        """ % _OBJECT_TYPE_NOTE

        return await api(
            get_client,
            "GET",
            f"/crm/v3/objects/{object_type}",
            params={
                "limit": limit,
                "after": after,
                "properties": properties,
                "associations": associations,
                "archived": archived,
            },
        )

    @mcp.tool()
    async def hubspot_get_object(
        object_type: str,
        object_id: str,
        properties: list[str] | None = None,
        associations: list[str] | None = None,
        id_property: str | None = None,
        archived: bool = False,
    ) -> dict[str, Any]:
        """Fetch a single CRM record by ID.

        Args:
            object_type: %s
            object_id: The record ID, or the value of ``id_property`` if set.
            properties: Property names to return.
            associations: Object types to return associated record IDs for.
            id_property: A unique property to look up by instead of the record
                ID (e.g. 'email' for contacts).
            archived: Look in archived records.
        """ % _OBJECT_TYPE_NOTE

        return await api(
            get_client,
            "GET",
            f"/crm/v3/objects/{object_type}/{object_id}",
            params={
                "properties": properties,
                "associations": associations,
                "idProperty": id_property,
                "archived": archived,
            },
        )

    @mcp.tool()
    async def hubspot_create_object(
        object_type: str,
        properties: dict[str, Any],
        associations: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a new CRM record.

        Args:
            object_type: %s
            properties: Map of property name -> value, e.g.
                {"email": "a@b.com", "firstname": "Ada"}.
            associations: Optional list of association objects to link the new
                record to existing records on creation. Each item looks like
                {"to": {"id": "123"}, "types": [{"associationCategory":
                "HUBSPOT_DEFINED", "associationTypeId": 1}]}.
        """ % _OBJECT_TYPE_NOTE

        body: dict[str, Any] = {"properties": properties}
        if associations:
            body["associations"] = associations
        return await api(get_client, "POST", f"/crm/v3/objects/{object_type}", json=body)

    @mcp.tool()
    async def hubspot_update_object(
        object_type: str,
        object_id: str,
        properties: dict[str, Any],
        id_property: str | None = None,
    ) -> dict[str, Any]:
        """Update properties on an existing CRM record.

        Args:
            object_type: %s
            object_id: The record ID (or value of ``id_property``).
            properties: Map of property name -> new value.
            id_property: A unique property to identify the record by instead of
                the record ID.
        """ % _OBJECT_TYPE_NOTE

        return await api(
            get_client,
            "PATCH",
            f"/crm/v3/objects/{object_type}/{object_id}",
            params={"idProperty": id_property},
            json={"properties": properties},
        )

    @mcp.tool()
    async def hubspot_delete_object(object_type: str, object_id: str) -> dict[str, Any]:
        """Archive (soft-delete) a CRM record.

        Args:
            object_type: %s
            object_id: The record ID to archive.

        Returns:
            A confirmation dict (HubSpot returns no body for this call).
        """ % _OBJECT_TYPE_NOTE

        await api(get_client, "DELETE", f"/crm/v3/objects/{object_type}/{object_id}")
        return {"archived": True, "object_type": object_type, "id": object_id}

    @mcp.tool()
    async def hubspot_search_objects(
        object_type: str,
        query: str | None = None,
        filter_groups: list[dict[str, Any]] | None = None,
        properties: list[str] | None = None,
        sorts: list[dict[str, Any]] | None = None,
        limit: int = 25,
        after: str | None = None,
    ) -> dict[str, Any]:
        """Search CRM records with filters and/or full-text query.

        Args:
            object_type: %s
            query: Free-text search string matched across default searchable
                properties.
            filter_groups: HubSpot filter groups (OR of groups, AND within a
                group). Each filter is like
                {"propertyName": "email", "operator": "EQ", "value": "a@b.com"}.
                Operators include EQ, NEQ, LT, LTE, GT, GTE, BETWEEN, IN, NOT_IN,
                HAS_PROPERTY, NOT_HAS_PROPERTY, CONTAINS_TOKEN, NOT_CONTAINS_TOKEN.
            properties: Property names to return for each match.
            sorts: Sort directives, e.g.
                [{"propertyName": "createdate", "direction": "DESCENDING"}].
            limit: Page size, max 200 (default 25).
            after: Pagination cursor.
        """ % _OBJECT_TYPE_NOTE

        body: dict[str, Any] = {"limit": limit}
        if query is not None:
            body["query"] = query
        if filter_groups is not None:
            body["filterGroups"] = filter_groups
        if properties is not None:
            body["properties"] = properties
        if sorts is not None:
            body["sorts"] = sorts
        if after is not None:
            body["after"] = after
        return await api(
            get_client, "POST", f"/crm/v3/objects/{object_type}/search", json=body
        )

    @mcp.tool()
    async def hubspot_batch_read_objects(
        object_type: str,
        ids: list[str],
        properties: list[str] | None = None,
        id_property: str | None = None,
    ) -> dict[str, Any]:
        """Read many CRM records by ID in a single request.

        Args:
            object_type: %s
            ids: Record IDs (or values of ``id_property``) to read, max 100.
            properties: Property names to return.
            id_property: Unique property to identify records by.
        """ % _OBJECT_TYPE_NOTE

        body: dict[str, Any] = {"inputs": [{"id": i} for i in ids]}
        if properties is not None:
            body["properties"] = properties
        if id_property is not None:
            body["idProperty"] = id_property
        return await api(
            get_client, "POST", f"/crm/v3/objects/{object_type}/batch/read", json=body
        )
