"""
Gmail OAuth 2.0 authentication with token caching.

On first run the browser opens for consent.  The resulting credentials
are persisted to ``token.json`` so subsequent runs skip the browser.
"""

import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from typing import Optional

from config import CREDENTIALS_FILE, TOKEN_FILE, GMAIL_SCOPES

logger = logging.getLogger(__name__)


def gmail_authenticate() -> Resource:
    """Authenticate with Gmail and return an API service object.

    Loads cached credentials from *token.json* when available, refreshes
    them if expired, and falls back to the full OAuth browser flow only
    when no valid token exists.

    Returns:
        A ``googleapiclient.discovery.Resource`` for the Gmail v1 API.

    Raises:
        FileNotFoundError: If ``credentials.json`` is missing.
        google.auth.exceptions.RefreshError: If the stored token cannot
            be refreshed (user revoked access, etc.).
    """
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(
            f"OAuth credentials file not found: {CREDENTIALS_FILE}\n"
            "Download it from the Google Cloud Console."
        )

    creds: Optional[Credentials] = None

    # 1. Try loading cached token
    if TOKEN_FILE.exists():
        logger.info("🔑 Loading cached OAuth token …")
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), GMAIL_SCOPES)

    # 2. Refresh or acquire new credentials
    if creds and creds.expired and creds.refresh_token:
        logger.info("🔄 Refreshing expired OAuth token …")
        creds.refresh(Request())
    elif not creds or not creds.valid:
        logger.info("🌐 Starting OAuth browser flow …")
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE), GMAIL_SCOPES
        )
        creds = flow.run_local_server(port=0)

    # 3. Persist token for next run
    TOKEN_FILE.write_text(creds.to_json())
    logger.info("✅ Gmail authentication successful")

    return build("gmail", "v1", credentials=creds)


if __name__ == "__main__":
    from config import setup_logging
    setup_logging()
    gmail_authenticate()