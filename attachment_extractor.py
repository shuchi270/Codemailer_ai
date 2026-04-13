"""
Email attachment extractor.

Downloads code-file attachments from Gmail messages into a dedicated
``attachments/`` directory, with filename sanitization and per-file
error isolation.
"""

import base64
import logging
import re
from pathlib import Path
from typing import Any, Dict, List

from googleapiclient.discovery import Resource

from config import ATTACHMENTS_DIR

logger = logging.getLogger(__name__)


def _sanitize_filename(name: str) -> str:
    """Remove path-traversal characters and whitespace from a filename."""
    name = Path(name).name                      # strip directory components
    name = re.sub(r"[^\w.\-]", "_", name)       # replace unsafe chars
    return name or "unnamed_attachment"


def _get_all_parts(parts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Recursively flatten nested MIME parts."""
    flat: List[Dict[str, Any]] = []
    for part in parts:
        flat.append(part)
        if "parts" in part:
            flat.extend(_get_all_parts(part["parts"]))
    return flat


def extract_attachments(
    service: Resource,
    message: Dict[str, Any],
) -> List[Path]:
    """Download all attachments from a Gmail message.

    Files are saved into the ``attachments/`` subdirectory.  Each
    attachment is handled independently — a failure on one does not
    block the others.

    Args:
        service: Authenticated Gmail API service object.
        message: Full Gmail message resource dict.

    Returns:
        A list of ``Path`` objects pointing to the downloaded files.
    """
    logger.info("📎 Extracting attachments …")
    ATTACHMENTS_DIR.mkdir(exist_ok=True)

    payload = message.get("payload", {})
    parts = _get_all_parts(payload.get("parts", [])) if "parts" in payload else [payload]

    downloaded: List[Path] = []

    for part in parts:
        raw_filename = part.get("filename")
        if not raw_filename:
            continue

        filename = _sanitize_filename(raw_filename)
        attachment_id = part.get("body", {}).get("attachmentId")
        if not attachment_id:
            logger.warning("⚠️ Skipping %s — no attachment ID", filename)
            continue

        try:
            logger.info("⬇️  Downloading: %s", filename)
            attachment = service.users().messages().attachments().get(
                userId="me",
                messageId=message["id"],
                id=attachment_id,
            ).execute()

            data = base64.urlsafe_b64decode(attachment["data"].encode("UTF-8"))
            file_path = ATTACHMENTS_DIR / filename

            file_path.write_bytes(data)
            downloaded.append(file_path)

        except Exception:
            logger.error("❌ Failed to download %s", filename, exc_info=True)

    if downloaded:
        logger.info("✅ Extracted %d file(s)", len(downloaded))
    else:
        logger.info("⚠️ No attachments found")

    return downloaded


def cleanup_attachments(files: List[Path]) -> None:
    """Delete previously downloaded attachment files.

    Args:
        files: Paths returned by :func:`extract_attachments`.
    """
    for path in files:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            logger.debug("Could not remove %s", path, exc_info=True)