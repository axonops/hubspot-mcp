"""Marketing Email tools.

Create, manage, publish, and report on marketing emails. Marketing emails are
identified by a numeric ``emailId`` and move through draft -> published states.
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_list_marketing_emails(
        limit: int = 100,
        after: str | None = None,
        created_after: str | None = None,
        sort: str | None = None,
        archived: bool = False,
    ) -> dict[str, Any]:
        """List marketing emails.

        Args:
            limit: Page size (default 100).
            after: Pagination cursor.
            created_after: ISO-8601 time; only return emails created after this.
            sort: Property to sort by; prefix '-' for descending.
            archived: Return archived emails.
        """

        return await api(
            get_client,
            "GET",
            "/marketing/v3/emails",
            params={
                "limit": limit,
                "after": after,
                "createdAfter": created_after,
                "sort": sort,
                "archived": archived,
            },
        )

    @mcp.tool()
    async def hubspot_get_marketing_email(
        email_id: str, properties: list[str] | None = None
    ) -> dict[str, Any]:
        """Get a marketing email by ID.

        Args:
            email_id: The marketing email ID.
            properties: Specific fields to include.
        """

        return await api(
            get_client,
            "GET",
            f"/marketing/v3/emails/{email_id}",
            params={"properties": properties},
        )

    @mcp.tool()
    async def hubspot_create_marketing_email(
        name: str,
        subject: str | None = None,
        from_details: dict[str, Any] | None = None,
        to_details: dict[str, Any] | None = None,
        content: dict[str, Any] | None = None,
        campaign: str | None = None,
        subscription_details: dict[str, Any] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a marketing email (in draft state).

        Args:
            name: Internal email name (required).
            subject: Subject line.
            from_details: Sender info, e.g.
                {"fromName": "Acme", "replyTo": "hi@acme.com"}.
            to_details: Recipient targeting (lists/segments).
            content: Email content object (e.g. {"templatePath": ...} or
                {"widgets": {...}, "styleSettings": {...}}).
            campaign: Campaign GUID to associate the email with.
            subscription_details: Subscription/legal settings, e.g.
                {"subscriptionName": ..., "officeLocationName": ...}.
            extra: Any additional top-level fields from the HubSpot email schema
                (merged into the request body).
        """

        body: dict[str, Any] = {"name": name}
        if subject is not None:
            body["subject"] = subject
        if from_details is not None:
            body["from"] = from_details
        if to_details is not None:
            body["to"] = to_details
        if content is not None:
            body["content"] = content
        if campaign is not None:
            body["campaign"] = campaign
        if subscription_details is not None:
            body["subscriptionDetails"] = subscription_details
        if extra:
            body.update(extra)
        return await api(get_client, "POST", "/marketing/v3/emails", json=body)

    @mcp.tool()
    async def hubspot_update_marketing_email(
        email_id: str, updates: dict[str, Any]
    ) -> dict[str, Any]:
        """Update fields on a marketing email.

        Args:
            email_id: The marketing email ID.
            updates: Top-level fields to change (e.g. {"name": ..., "subject":
                ..., "content": {...}}).
        """

        return await api(
            get_client, "PATCH", f"/marketing/v3/emails/{email_id}", json=updates
        )

    @mcp.tool()
    async def hubspot_delete_marketing_email(email_id: str) -> dict[str, Any]:
        """Delete (archive) a marketing email.

        Args:
            email_id: The marketing email ID.
        """

        await api(get_client, "DELETE", f"/marketing/v3/emails/{email_id}")
        return {"deleted": True, "emailId": email_id}

    @mcp.tool()
    async def hubspot_clone_marketing_email(
        email_id: str, clone_name: str | None = None
    ) -> dict[str, Any]:
        """Clone a marketing email.

        Args:
            email_id: ID of the email to clone.
            clone_name: Optional name for the clone.
        """

        body: dict[str, Any] = {"id": email_id}
        if clone_name is not None:
            body["cloneName"] = clone_name
        return await api(get_client, "POST", "/marketing/v3/emails/clone", json=body)

    @mcp.tool()
    async def hubspot_publish_marketing_email(email_id: str) -> dict[str, Any]:
        """Publish / schedule a marketing email for sending.

        Args:
            email_id: The marketing email ID.
        """

        return await api(
            get_client, "POST", f"/marketing/v3/emails/{email_id}/publish"
        )

    @mcp.tool()
    async def hubspot_unpublish_marketing_email(email_id: str) -> dict[str, Any]:
        """Cancel a scheduled send / unpublish a marketing email.

        Args:
            email_id: The marketing email ID.
        """

        return await api(
            get_client, "POST", f"/marketing/v3/emails/{email_id}/unpublish"
        )

    @mcp.tool()
    async def hubspot_get_marketing_email_statistics(
        email_ids: list[str] | None = None,
        start_timestamp: str | None = None,
        end_timestamp: str | None = None,
    ) -> dict[str, Any]:
        """Get aggregated send/open/click statistics for marketing emails.

        Args:
            email_ids: Specific email IDs to include (omit for all).
            start_timestamp: ISO-8601 start of the reporting window.
            end_timestamp: ISO-8601 end of the reporting window.
        """

        return await api(
            get_client,
            "GET",
            "/marketing/v3/emails/statistics/list",
            params={
                "emailIds": email_ids,
                "startTimestamp": start_timestamp,
                "endTimestamp": end_timestamp,
            },
        )
