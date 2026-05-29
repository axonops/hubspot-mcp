"""CRM association tools (Associations v4 API).

Associations link records together, e.g. a contact to a company, or a note to
a deal. Most links use a "default" (HubSpot-defined) association; labelled
associations let you attach specific relationship types.
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_list_associations(
        object_type: str,
        object_id: str,
        to_object_type: str,
        limit: int = 100,
        after: str | None = None,
    ) -> dict[str, Any]:
        """List records of one type associated with a given record.

        Args:
            object_type: Type of the source record (e.g. 'contacts').
            object_id: ID of the source record.
            to_object_type: Type of associated records to return (e.g. 'companies').
            limit: Page size (default 100).
            after: Pagination cursor.
        """

        return await api(
            get_client,
            "GET",
            f"/crm/v4/objects/{object_type}/{object_id}/associations/{to_object_type}",
            params={"limit": limit, "after": after},
        )

    @mcp.tool()
    async def hubspot_associate_default(
        from_object_type: str,
        from_object_id: str,
        to_object_type: str,
        to_object_id: str,
    ) -> dict[str, Any]:
        """Create the default association between two records.

        Use this for the common case of simply linking two records (HubSpot
        picks the standard association type for the pair).

        Args:
            from_object_type: Source record type (e.g. 'contacts').
            from_object_id: Source record ID.
            to_object_type: Target record type (e.g. 'companies').
            to_object_id: Target record ID.
        """

        return await api(
            get_client,
            "PUT",
            f"/crm/v4/objects/{from_object_type}/{from_object_id}"
            f"/associations/default/{to_object_type}/{to_object_id}",
        )

    @mcp.tool()
    async def hubspot_associate_labeled(
        from_object_type: str,
        from_object_id: str,
        to_object_type: str,
        to_object_id: str,
        association_types: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Create a labelled / specific-type association between two records.

        Args:
            from_object_type: Source record type.
            from_object_id: Source record ID.
            to_object_type: Target record type.
            to_object_id: Target record ID.
            association_types: List of association type specs, e.g.
                [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 1}].
                Use hubspot_list_association_labels to discover valid type IDs.
        """

        return await api(
            get_client,
            "PUT",
            f"/crm/v4/objects/{from_object_type}/{from_object_id}"
            f"/associations/{to_object_type}/{to_object_id}",
            json=association_types,
        )

    @mcp.tool()
    async def hubspot_delete_association(
        from_object_type: str,
        from_object_id: str,
        to_object_type: str,
        to_object_id: str,
    ) -> dict[str, Any]:
        """Remove all associations between two records.

        Args:
            from_object_type: Source record type.
            from_object_id: Source record ID.
            to_object_type: Target record type.
            to_object_id: Target record ID.
        """

        await api(
            get_client,
            "DELETE",
            f"/crm/v4/objects/{from_object_type}/{from_object_id}"
            f"/associations/{to_object_type}/{to_object_id}",
        )
        return {
            "deleted": True,
            "from": {"type": from_object_type, "id": from_object_id},
            "to": {"type": to_object_type, "id": to_object_id},
        }

    @mcp.tool()
    async def hubspot_list_association_labels(
        from_object_type: str, to_object_type: str
    ) -> dict[str, Any]:
        """List the association types/labels available between two object types.

        Use this to find ``associationTypeId`` values for
        hubspot_associate_labeled.

        Args:
            from_object_type: Source object type.
            to_object_type: Target object type.
        """

        return await api(
            get_client,
            "GET",
            f"/crm/associations/v4/{from_object_type}/{to_object_type}/labels",
        )
