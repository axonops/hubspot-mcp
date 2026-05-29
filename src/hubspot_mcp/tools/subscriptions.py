"""Communication preferences (subscription) tools.

Manage GDPR-style email subscription preferences: discover subscription types,
check a contact's status, and subscribe/unsubscribe addresses.
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_list_subscription_definitions() -> dict[str, Any]:
        """List the subscription types (definitions) configured in the account.

        Use the returned IDs as ``subscription_id`` when subscribing /
        unsubscribing.
        """

        return await api(
            get_client, "GET", "/communication-preferences/v3/definitions"
        )

    @mcp.tool()
    async def hubspot_get_subscription_status(email: str) -> dict[str, Any]:
        """Get the subscription status for an email address.

        Args:
            email: The email address to look up.
        """

        return await api(
            get_client, "GET", f"/communication-preferences/v3/status/email/{email}"
        )

    @mcp.tool()
    async def hubspot_subscribe(
        email: str,
        subscription_id: str,
        legal_basis: str | None = None,
        legal_basis_explanation: str | None = None,
    ) -> dict[str, Any]:
        """Opt an email address in to a subscription type.

        Args:
            email: The email address.
            subscription_id: The subscription definition ID.
            legal_basis: Optional legal basis, e.g.
                'CONSENT_WITH_NOTICE', 'LEGITIMATE_INTEREST_PQL'.
            legal_basis_explanation: Free-text explanation for the legal basis.
        """

        body: dict[str, Any] = {"emailAddress": email, "subscriptionId": subscription_id}
        if legal_basis is not None:
            body["legalBasis"] = legal_basis
        if legal_basis_explanation is not None:
            body["legalBasisExplanation"] = legal_basis_explanation
        return await api(
            get_client, "POST", "/communication-preferences/v3/subscribe", json=body
        )

    @mcp.tool()
    async def hubspot_unsubscribe(
        email: str,
        subscription_id: str,
        legal_basis: str | None = None,
        legal_basis_explanation: str | None = None,
    ) -> dict[str, Any]:
        """Opt an email address out of a subscription type.

        Args:
            email: The email address.
            subscription_id: The subscription definition ID.
            legal_basis: Optional legal basis string.
            legal_basis_explanation: Free-text explanation for the legal basis.
        """

        body: dict[str, Any] = {"emailAddress": email, "subscriptionId": subscription_id}
        if legal_basis is not None:
            body["legalBasis"] = legal_basis
        if legal_basis_explanation is not None:
            body["legalBasisExplanation"] = legal_basis_explanation
        return await api(
            get_client, "POST", "/communication-preferences/v3/unsubscribe", json=body
        )
