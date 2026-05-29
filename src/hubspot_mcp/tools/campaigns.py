"""Marketing Campaigns tools.

Campaigns group marketing assets (emails, forms, social posts, ads, etc.) and
expose reporting on contacts, revenue, and engagement metrics. Campaigns are
identified by a ``campaignGuid``.
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_list_campaigns(
        limit: int = 100,
        after: str | None = None,
        properties: list[str] | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        """List marketing campaigns.

        Args:
            limit: Page size (default 100).
            after: Pagination cursor.
            properties: Campaign properties to return (e.g. ["hs_name",
                "hs_start_date", "hs_end_date", "hs_goal"]).
            sort: Property to sort by, prefix with '-' for descending.
        """

        return await api(
            get_client,
            "GET",
            "/marketing/v3/campaigns",
            params={"limit": limit, "after": after, "properties": properties, "sort": sort},
        )

    @mcp.tool()
    async def hubspot_get_campaign(
        campaign_guid: str, properties: list[str] | None = None
    ) -> dict[str, Any]:
        """Get a single campaign by GUID.

        Args:
            campaign_guid: The campaign's GUID.
            properties: Campaign properties to return.
        """

        return await api(
            get_client,
            "GET",
            f"/marketing/v3/campaigns/{campaign_guid}",
            params={"properties": properties},
        )

    @mcp.tool()
    async def hubspot_create_campaign(properties: dict[str, Any]) -> dict[str, Any]:
        """Create a marketing campaign.

        Args:
            properties: Campaign properties. ``hs_name`` is the campaign name
                (required). Other common keys: hs_start_date, hs_end_date,
                hs_goal, hs_currency_code, hs_owner, hs_budget_items_sum_amount.
        """

        return await api(
            get_client, "POST", "/marketing/v3/campaigns", json={"properties": properties}
        )

    @mcp.tool()
    async def hubspot_update_campaign(
        campaign_guid: str, properties: dict[str, Any]
    ) -> dict[str, Any]:
        """Update properties on a campaign.

        Args:
            campaign_guid: The campaign's GUID.
            properties: Map of campaign property -> new value.
        """

        return await api(
            get_client,
            "PATCH",
            f"/marketing/v3/campaigns/{campaign_guid}",
            json={"properties": properties},
        )

    @mcp.tool()
    async def hubspot_delete_campaign(campaign_guid: str) -> dict[str, Any]:
        """Delete (archive) a campaign.

        Args:
            campaign_guid: The campaign's GUID.
        """

        await api(get_client, "DELETE", f"/marketing/v3/campaigns/{campaign_guid}")
        return {"deleted": True, "campaignGuid": campaign_guid}

    @mcp.tool()
    async def hubspot_list_campaign_asset_types() -> dict[str, Any]:
        """List the asset types that can be attached to a campaign.

        (e.g. EMAIL, FORM, SOCIAL_POST, AD_CAMPAIGN, LANDING_PAGE, etc.)
        """

        return await api(get_client, "GET", "/marketing/campaigns/v3/asset-types")

    @mcp.tool()
    async def hubspot_list_campaign_assets(
        campaign_guid: str, asset_type: str, limit: int = 100, after: str | None = None
    ) -> dict[str, Any]:
        """List assets of a given type attached to a campaign.

        Args:
            campaign_guid: The campaign's GUID.
            asset_type: Asset type, e.g. 'EMAIL', 'FORM', 'LANDING_PAGE'.
            limit: Page size.
            after: Pagination cursor.
        """

        return await api(
            get_client,
            "GET",
            f"/marketing/v3/campaigns/{campaign_guid}/assets/{asset_type}",
            params={"limit": limit, "after": after},
        )

    @mcp.tool()
    async def hubspot_add_campaign_asset(
        campaign_guid: str, asset_type: str, asset_id: str
    ) -> dict[str, Any]:
        """Attach an existing asset to a campaign.

        Args:
            campaign_guid: The campaign's GUID.
            asset_type: Asset type, e.g. 'EMAIL', 'FORM'.
            asset_id: ID of the asset to attach.
        """

        await api(
            get_client,
            "PUT",
            f"/marketing/v3/campaigns/{campaign_guid}/assets/{asset_type}/{asset_id}",
        )
        return {"attached": True, "campaignGuid": campaign_guid, "assetType": asset_type, "assetId": asset_id}

    @mcp.tool()
    async def hubspot_remove_campaign_asset(
        campaign_guid: str, asset_type: str, asset_id: str
    ) -> dict[str, Any]:
        """Detach an asset from a campaign.

        Args:
            campaign_guid: The campaign's GUID.
            asset_type: Asset type.
            asset_id: ID of the asset to detach.
        """

        await api(
            get_client,
            "DELETE",
            f"/marketing/v3/campaigns/{campaign_guid}/assets/{asset_type}/{asset_id}",
        )
        return {"detached": True, "campaignGuid": campaign_guid, "assetType": asset_type, "assetId": asset_id}

    @mcp.tool()
    async def hubspot_get_campaign_metrics(
        campaign_guid: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Get aggregated engagement metrics for a campaign.

        Args:
            campaign_guid: The campaign's GUID.
            start_date: Optional YYYY-MM-DD start of the reporting window.
            end_date: Optional YYYY-MM-DD end of the reporting window.
        """

        return await api(
            get_client,
            "GET",
            f"/marketing/v3/campaigns/{campaign_guid}/reports/metrics",
            params={"startDate": start_date, "endDate": end_date},
        )

    @mcp.tool()
    async def hubspot_get_campaign_revenue(
        campaign_guid: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Get revenue attribution for a campaign.

        Args:
            campaign_guid: The campaign's GUID.
            start_date: Optional YYYY-MM-DD start of the reporting window.
            end_date: Optional YYYY-MM-DD end of the reporting window.
        """

        return await api(
            get_client,
            "GET",
            f"/marketing/v3/campaigns/{campaign_guid}/reports/revenue",
            params={"startDate": start_date, "endDate": end_date},
        )

    @mcp.tool()
    async def hubspot_get_campaign_contacts(
        campaign_guid: str,
        contact_type: str,
        limit: int = 100,
        after: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """List contacts of a given type influenced by a campaign.

        Args:
            campaign_guid: The campaign's GUID.
            contact_type: One of 'influenced', 'contactsFirstTouch',
                'contactsLastTouch'.
            limit: Page size.
            after: Pagination cursor.
            start_date: Optional YYYY-MM-DD start of the window.
            end_date: Optional YYYY-MM-DD end of the window.
        """

        return await api(
            get_client,
            "GET",
            f"/marketing/v3/campaigns/{campaign_guid}/reports/contacts/{contact_type}",
            params={"limit": limit, "after": after, "startDate": start_date, "endDate": end_date},
        )
