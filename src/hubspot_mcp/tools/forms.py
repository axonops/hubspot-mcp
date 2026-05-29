"""Marketing Forms tools.

Create and manage HubSpot forms used to capture leads. Form definitions are
rich objects (field groups, configuration, display options); create/update
accept the full definition so any form type can be expressed.
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_list_forms(
        limit: int = 100, after: str | None = None
    ) -> dict[str, Any]:
        """List marketing forms.

        Args:
            limit: Page size (default 100).
            after: Pagination cursor.
        """

        return await api(
            get_client, "GET", "/marketing/v3/forms", params={"limit": limit, "after": after}
        )

    @mcp.tool()
    async def hubspot_get_form(form_id: str) -> dict[str, Any]:
        """Get a form definition by ID.

        Args:
            form_id: The form's ID (GUID).
        """

        return await api(get_client, "GET", f"/marketing/v3/forms/{form_id}")

    @mcp.tool()
    async def hubspot_create_form(form_definition: dict[str, Any]) -> dict[str, Any]:
        """Create a form.

        Args:
            form_definition: Full HubSpot form definition. Minimal example:
                {"name": "Contact us", "formType": "hubspot",
                 "fieldGroups": [{"fields": [{"objectTypeId": "0-1",
                 "name": "email", "fieldType": "email", "required": true,
                 "label": "Email"}]}],
                 "configuration": {"language": "en"}}.
        """

        return await api(get_client, "POST", "/marketing/v3/forms", json=form_definition)

    @mcp.tool()
    async def hubspot_update_form(
        form_id: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a form (partial update).

        Args:
            form_id: The form's ID.
            updates: Fields of the form definition to change.
        """

        return await api(
            get_client, "PATCH", f"/marketing/v3/forms/{form_id}", json=updates
        )

    @mcp.tool()
    async def hubspot_delete_form(form_id: str) -> dict[str, Any]:
        """Delete a form.

        Args:
            form_id: The form's ID.
        """

        await api(get_client, "DELETE", f"/marketing/v3/forms/{form_id}")
        return {"deleted": True, "formId": form_id}
