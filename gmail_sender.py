"""
Gmail reply sender.

Composes and sends an HTML email back to the original code submitter.
"""

import base64
import logging
from email.mime.text import MIMEText
from typing import Optional

from googleapiclient.discovery import Resource

logger = logging.getLogger(__name__)


def _compose_html_message(
    to: str,
    subject: str,
    html_body: str,
) -> dict:
    """Build a Gmail-compatible raw message dict.

    Args:
        to: Recipient email address.
        subject: Email subject line.
        html_body: HTML string for the email body.

    Returns:
        A dict with a ``"raw"`` key ready for the Gmail send API.
    """
    msg = MIMEText(html_body, "html")
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def send_reply(
    service: Resource,
    to_email: str,
    html_report: str,
    subject: str = "Code Analysis Report — CodeMailer AI",
) -> bool:
    """Send an HTML report email.

    Args:
        service: Authenticated Gmail API service object.
        to_email: Recipient email address.
        html_report: Rendered HTML report string.
        subject: Email subject line.

    Returns:
        ``True`` on success, ``False`` on failure.
    """
    logger.info("📤 Sending report to %s …", to_email)

    try:
        body = _compose_html_message(to_email, subject, html_report)
        service.users().messages().send(userId="me", body=body).execute()
        logger.info("✅ Reply sent successfully")
        return True
    except Exception:
        logger.error("❌ Failed to send reply to %s", to_email, exc_info=True)
        return False