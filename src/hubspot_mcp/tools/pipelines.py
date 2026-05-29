"""CRM pipeline tools.

Pipelines and their stages model the lifecycle of deals, tickets, and other
object types (e.g. deal stages like "appointmentscheduled" -> "closedwon").
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_list_pipelines(object_type: str) -> dict[str, Any]:
        """List all pipelines for an object type.

        Args:
            object_type: Object type with pipelines, e.g. 'deals' or 'tickets'.
        """

        return await api(get_client, "GET", f"/crm/v3/pipelines/{object_type}")

    @mcp.tool()
    async def hubspot_get_pipeline(object_type: str, pipeline_id: str) -> dict[str, Any]:
        """Get a single pipeline, including its stages.

        Args:
            object_type: Object type the pipeline belongs to (e.g. 'deals').
            pipeline_id: The pipeline ID.
        """

        return await api(
            get_client, "GET", f"/crm/v3/pipelines/{object_type}/{pipeline_id}"
        )

    @mcp.tool()
    async def hubspot_list_pipeline_stages(
        object_type: str, pipeline_id: str
    ) -> dict[str, Any]:
        """List the stages of a pipeline.

        Args:
            object_type: Object type the pipeline belongs to.
            pipeline_id: The pipeline ID.
        """

        return await api(
            get_client, "GET", f"/crm/v3/pipelines/{object_type}/{pipeline_id}/stages"
        )
