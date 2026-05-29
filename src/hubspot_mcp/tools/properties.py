"""CRM property (schema) tools.

Properties define the fields available on each object type. Use these to
discover what data you can read/write, or to create new custom properties.
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_list_properties(
        object_type: str, archived: bool = False
    ) -> dict[str, Any]:
        """List all properties (fields) defined for an object type.

        Args:
            object_type: e.g. 'contacts', 'companies', 'deals', 'tickets', or a
                custom object type.
            archived: Return archived properties instead of active ones.
        """

        return await api(
            get_client,
            "GET",
            f"/crm/v3/properties/{object_type}",
            params={"archived": archived},
        )

    @mcp.tool()
    async def hubspot_get_property(
        object_type: str, property_name: str
    ) -> dict[str, Any]:
        """Get the definition of a single property, including its options.

        Args:
            object_type: The object type the property belongs to.
            property_name: The internal property name (e.g. 'lifecyclestage').
        """

        return await api(
            get_client, "GET", f"/crm/v3/properties/{object_type}/{property_name}"
        )

    @mcp.tool()
    async def hubspot_create_property(
        object_type: str,
        name: str,
        label: str,
        type: str,
        field_type: str,
        group_name: str | None = None,
        description: str | None = None,
        options: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Create a new custom property on an object type.

        Args:
            object_type: The object type to add the property to.
            name: Internal name (lowercase, no spaces), e.g. 'my_custom_field'.
            label: Human-readable label shown in the UI.
            type: Data type: 'string', 'number', 'date', 'datetime', 'enumeration',
                or 'bool'.
            field_type: UI control: 'text', 'textarea', 'number', 'select',
                'radio', 'checkbox', 'booleancheckbox', 'date', 'file', etc.
            group_name: Property group to place it in (e.g. 'contactinformation').
            description: Optional description.
            options: For enumeration types, a list of
                {"label": "...", "value": "...", "displayOrder": 0}.
        """

        body: dict[str, Any] = {
            "name": name,
            "label": label,
            "type": type,
            "fieldType": field_type,
        }
        if group_name is not None:
            body["groupName"] = group_name
        if description is not None:
            body["description"] = description
        if options is not None:
            body["options"] = options
        return await api(
            get_client, "POST", f"/crm/v3/properties/{object_type}", json=body
        )
