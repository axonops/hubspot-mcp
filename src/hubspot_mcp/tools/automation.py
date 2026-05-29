"""Automation / Workflow (Flows v4) tools.

Read and inspect HubSpot automation flows (workflows) and their performance.
Flows are the engine behind marketing automation — enrollment, delays, email
sends, branching, etc.
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_list_flows(
        limit: int = 100, after: str | None = None
    ) -> dict[str, Any]:
        """List automation flows (workflows).

        Args:
            limit: Page size (default 100).
            after: Pagination cursor.
        """

        return await api(
            get_client,
            "GET",
            "/automation/v4/flows",
            params={"limit": limit, "after": after},
        )

    @mcp.tool()
    async def hubspot_get_flow(flow_id: str) -> dict[str, Any]:
        """Get the full definition of a single automation flow.

        Args:
            flow_id: The flow's ID.
        """

        return await api(get_client, "GET", f"/automation/v4/flows/{flow_id}")

    @mcp.tool()
    async def hubspot_get_flow_performance(
        flow_id: str, start_time: str | None = None, end_time: str | None = None
    ) -> dict[str, Any]:
        """Get performance/enrollment metrics for a flow.

        Args:
            flow_id: The flow's ID.
            start_time: Optional ISO-8601 / epoch-ms start of the window.
            end_time: Optional ISO-8601 / epoch-ms end of the window.
        """

        return await api(
            get_client,
            "GET",
            f"/automation/v4/flows/performance/{flow_id}",
            params={"startTime": start_time, "endTime": end_time},
        )

    @mcp.tool()
    async def hubspot_list_email_campaign_flows(
        limit: int = 100, after: str | None = None
    ) -> dict[str, Any]:
        """List flows that drive email campaigns.

        Args:
            limit: Page size.
            after: Pagination cursor.
        """

        return await api(
            get_client,
            "GET",
            "/automation/v4/flows/email-campaigns",
            params={"limit": limit, "after": after},
        )
