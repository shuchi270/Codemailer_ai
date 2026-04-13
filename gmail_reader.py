"""
Gmail message reading utilities.

Provides functions to list unread messages and fetch individual
email content from the Gmail API.
"""

import logging
from typing import Any, Dict, List

from googleapiclient.discovery import Resource

logger = logging.getLogger(__name__)


def get_unread_messages(service: Resource, max_results: int = 10) -> List[Dict[str, str]]:
    """Fetch unread message references from the inbox.

    Args:
        service: Authenticated Gmail API service object.
        max_results: Maximum number of messages to return.

    Returns:
        A list of dicts, each containing at least an ``"id"`` key.
    """
    logger.info("📥 Fetching unread emails …")

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        q="is:unread",
        maxResults=max_results,
    ).execute()

    messages: List[Dict[str, str]] = results.get("messages", [])
    logger.info("✅ Found %d unread email(s)", len(messages))
    return messages


def get_email_content(service: Resource, msg_id: str) -> Dict[str, Any]:
    """Fetch the full content of a single email message.

    Args:
        service: Authenticated Gmail API service object.
        msg_id: The Gmail message ID.

    Returns:
        The full message resource dict from the Gmail API.
    """
    logger.debug("📨 Fetching email content for ID: %s", msg_id)

    message: Dict[str, Any] = service.users().messages().get(
        userId="me",
        id=msg_id,
    ).execute()

    logger.debug("✅ Email content fetched")
    return message


def mark_as_read(service: Resource, msg_id: str) -> None:
    """Remove the UNREAD label from a message.

    Args:
        service: Authenticated Gmail API service object.
        msg_id: The Gmail message ID.
    """
    try:
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()
        logger.debug("📭 Marked message %s as read", msg_id)
    except Exception:
        logger.warning("⚠️ Failed to mark message %s as read", msg_id, exc_info=True)