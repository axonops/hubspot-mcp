"""Email sending tools.

Two ways to send email programmatically:

* **Transactional single-send** — for receipts, password resets, notifications
  (requires the transactional email add-on). Uses a transactional email's
  ``emailId``.
* **Marketing single-send (v4)** — send an existing automated marketing email
  to a single contact.
"""

from __future__ import annotations

from typing import Any

from ._base import ClientGetter, api


def register(mcp, get_client: ClientGetter) -> None:
    @mcp.tool()
    async def hubspot_send_transactional_email(
        email_id: int,
        to: str,
        from_: str | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        reply_to: list[str] | None = None,
        contact_properties: dict[str, Any] | None = None,
        custom_properties: dict[str, Any] | None = None,
        send_id: str | None = None,
    ) -> dict[str, Any]:
        """Send a transactional single-send email.

        Requires the transactional email add-on and a transactional email
        created in HubSpot.

        Args:
            email_id: Numeric ID of the transactional email to send.
            to: Recipient email address.
            from_: Optional From header override.
            cc: Cc email addresses.
            bcc: Bcc email addresses.
            reply_to: Reply-To header values.
            contact_properties: Contact properties to set/update on the
                recipient (keyed by property name).
            custom_properties: Custom merge values referenced by the email
                template (keyed by token name).
            send_id: Idempotency key — at most one email is sent per send_id.
        """

        message: dict[str, Any] = {"to": to}
        if from_ is not None:
            message["from"] = from_
        if cc is not None:
            message["cc"] = cc
        if bcc is not None:
            message["bcc"] = bcc
        if reply_to is not None:
            message["replyTo"] = reply_to
        if send_id is not None:
            message["sendId"] = send_id

        body: dict[str, Any] = {"emailId": email_id, "message": message}
        if contact_properties is not None:
            body["contactProperties"] = contact_properties
        if custom_properties is not None:
            body["customProperties"] = custom_properties
        return await api(
            get_client,
            "POST",
            "/marketing/v3/transactional/single-email/send",
            json=body,
        )

    @mcp.tool()
    async def hubspot_send_marketing_email(
        email_id: int,
        to: str,
        contact_properties: dict[str, Any] | None = None,
        custom_properties: dict[str, Any] | None = None,
        send_id: str | None = None,
    ) -> dict[str, Any]:
        """Send an existing automated marketing email to a single contact (v4).

        Args:
            email_id: Numeric ID of the marketing email (must be set up for
                automation / single-send).
            to: Recipient email address.
            contact_properties: Contact properties to set on the recipient.
            custom_properties: Custom merge values for the email template.
            send_id: Idempotency key.
        """

        message: dict[str, Any] = {"to": to}
        if send_id is not None:
            message["sendId"] = send_id
        body: dict[str, Any] = {"emailId": email_id, "message": message}
        if contact_properties is not None:
            body["contactProperties"] = contact_properties
        if custom_properties is not None:
            body["customProperties"] = custom_properties
        return await api(
            get_client, "POST", "/marketing/v4/email/single-send", json=body
        )
