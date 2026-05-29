"""Marketing Events tools.

Marketing events (webinars, conferences, etc.) and attendance/registration
state for contacts. Events have a HubSpot ``objectId`` and an
``externalEventId`` (your system's ID).
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_list_marketing_events(
        limit: int = 100, after: str | None = None
    ) -> dict[str, Any]:
        """List marketing events.

        Args:
            limit: Page size (default 100).
            after: Pagination cursor.
        """

        return await api(
            get_client,
            "GET",
            "/marketing/marketing-events/v3",
            params={"limit": limit, "after": after},
        )

    @mcp.tool()
    async def hubspot_search_marketing_events(
        q: str | None = None, limit: int = 100, after: str | None = None
    ) -> dict[str, Any]:
        """Search marketing events.

        Args:
            q: Search text matched against event fields.
            limit: Page size.
            after: Pagination cursor.
        """

        return await api(
            get_client,
            "GET",
            "/marketing/v3/marketing-events/events/search",
            params={"q": q, "limit": limit, "after": after},
        )

    @mcp.tool()
    async def hubspot_get_marketing_event(object_id: str) -> dict[str, Any]:
        """Get a marketing event by its HubSpot objectId.

        Args:
            object_id: The marketing event's HubSpot object ID.
        """

        return await api(
            get_client, "GET", f"/marketing/v3/marketing-events/{object_id}"
        )

    @mcp.tool()
    async def hubspot_upsert_marketing_events(
        inputs: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create or update marketing events in bulk (upsert by externalEventId).

        Args:
            inputs: List of event objects. Each needs ``externalEventId``,
                ``externalAccountId``, and an ``eventName``; other common fields
                include eventOrganizer, eventType, startDateTime, endDateTime,
                eventDescription, eventUrl, customProperties.
        """

        return await api(
            get_client,
            "POST",
            "/marketing/v3/marketing-events/events/upsert",
            json={"inputs": inputs},
        )

    @mcp.tool()
    async def hubspot_update_marketing_event(
        object_id: str, properties: dict[str, Any]
    ) -> dict[str, Any]:
        """Update a marketing event by HubSpot objectId.

        Args:
            object_id: The marketing event's HubSpot object ID.
            properties: Fields to update (e.g. eventName, startDateTime,
                eventDescription, customProperties).
        """

        return await api(
            get_client,
            "PATCH",
            f"/marketing/v3/marketing-events/{object_id}",
            json=properties,
        )

    @mcp.tool()
    async def hubspot_delete_marketing_event(object_id: str) -> dict[str, Any]:
        """Delete a marketing event by HubSpot objectId.

        Args:
            object_id: The marketing event's HubSpot object ID.
        """

        await api(get_client, "DELETE", f"/marketing/v3/marketing-events/{object_id}")
        return {"deleted": True, "objectId": object_id}

    @mcp.tool()
    async def hubspot_cancel_marketing_event(external_event_id: str) -> dict[str, Any]:
        """Mark a marketing event as cancelled.

        Args:
            external_event_id: The event's external ID.
        """

        return await api(
            get_client,
            "POST",
            f"/marketing/v3/marketing-events/events/{external_event_id}/cancel",
        )

    @mcp.tool()
    async def hubspot_record_marketing_event_attendance(
        object_id: str,
        subscriber_state: str,
        contacts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Record attendance/registration state for contacts on an event.

        Args:
            object_id: The marketing event's HubSpot object ID.
            subscriber_state: One of 'REGISTERED', 'ATTENDED', 'CANCELLED',
                'NO_SHOW'.
            contacts: List of contact identifiers with optional timestamps, e.g.
                [{"vid": 123}] or [{"email": "a@b.com",
                "interactionDateTime": 1699999999000}].
        """

        return await api(
            get_client,
            "POST",
            f"/marketing/v3/marketing-events/{object_id}/attendance/{subscriber_state}/create",
            json={"inputs": contacts},
        )
