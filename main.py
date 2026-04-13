"""
CodeMailer AI — main application entry point.

Provides:
- A Flask web server with ``/``, ``/run``, and ``/health`` endpoints.
- A ``run()`` pipeline that reads Gmail, analyses code attachments,
  generates reports, and replies to the sender.
"""

import logging
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from flask import Flask, jsonify
from pygments.lexers import guess_lexer_for_filename

from ai_analyzer import analyze_code
from attachment_extractor import cleanup_attachments, extract_attachments
from config import (
    FALLBACK_FILE,
    LANGUAGE_MAP,
    TEXT_EXTENSIONS,
    AppConfig,
    ensure_directories,
    setup_logging,
)
from gmail_auth import gmail_authenticate
from gmail_reader import get_email_content, get_unread_messages, mark_as_read
from gmail_sender import send_reply
from report_generator import generate_report

logger = logging.getLogger(__name__)


# ─── Data classes ────────────────────────────────────────────────

@dataclass
class EmailMeta:
    """Parsed metadata for a single email."""

    message_id: str
    subject: str
    sender: str

    @classmethod
    def from_message(cls, message: dict) -> "EmailMeta":
        headers = message.get("payload", {}).get("headers", [])
        header_map = {h["name"].lower(): h["value"] for h in headers}
        return cls(
            message_id=message.get("id", "N/A"),
            subject=header_map.get("subject", "(No Subject)"),
            sender=header_map.get("from", "Unknown Sender"),
        )

    @property
    def sender_email(self) -> str:
        """Extract the bare email address from the *From* header."""
        match = re.search(r"<([^>]+)>", self.sender)
        return match.group(1) if match else self.sender


# ─── File analysis helpers ───────────────────────────────────────

def _is_code_file(file_path: Path, content: str) -> bool:
    """Return True if the file looks like source code."""
    if file_path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    try:
        guess_lexer_for_filename(file_path.name, content)
        return True
    except Exception:
        return False


def _get_language(file_path: Path, content: str) -> str:
    """Map *file_path* to a human-readable language name."""
    ext = file_path.suffix.lower()
    if ext in LANGUAGE_MAP:
        return LANGUAGE_MAP[ext]
    try:
        return guess_lexer_for_filename(file_path.name, content).name
    except Exception:
        return "Unknown"


def _read_text(file_path: Path) -> Optional[str]:
    """Read file as UTF-8 text; return None on decode errors."""
    try:
        return file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def analyze_file(file_path: Path) -> Optional[str]:
    """Analyse a single source-code file.

    Returns a Markdown section string or *None* if the file is
    unreadable or not source code.
    """
    code = _read_text(file_path)
    if not code or not _is_code_file(file_path, code):
        return None

    logger.info("🤖 Analyzing %s …", file_path.name)

    lang = _get_language(file_path, code)
    lang_line = f"Detected language: {lang}\n\n" if lang != "Unknown" else ""

    analysis = analyze_code(code)
    return f"# File: {file_path.name}\n\n{lang_line}{analysis}"


# ─── Email processing ───────────────────────────────────────────

def _print_report(title: str, report_text: str) -> None:
    """Pretty-print an analysis report to the console."""
    separator = "=" * 50
    logger.info("\n%s\n%s\n%s\n%s\n%s", separator, title, separator, report_text, separator)


def process_email(service, message_ref: dict) -> Optional[tuple]:
    """Process a single unread email: extract → analyse → report.

    Returns:
        ``(markdown_report, EmailMeta)`` on success, or *None*.
    """
    message = get_email_content(service, message_ref["id"])
    meta = EmailMeta.from_message(message)
    logger.info("📧 Processing email: %s", meta.subject)

    downloaded_files = extract_attachments(service, message)
    analyses: List[str] = []

    try:
        for file_path in downloaded_files:
            if not file_path.exists():
                continue
            result = analyze_file(file_path)
            if result:
                analyses.append(result)
    finally:
        # Always clean up downloaded attachments
        cleanup_attachments(downloaded_files)

    if not analyses:
        return None

    email_summary = "\n".join([
        "### Email Details",
        f"**Subject:** {meta.subject}",
        f"**From:** {meta.sender}",
        f"**Message ID:** {meta.message_id}",
        "---",
    ])
    return email_summary + "\n\n" + "\n\n".join(analyses), meta


def run() -> None:
    """Execute the full CodeMailer AI pipeline."""
    logger.info("🚀 CodeMailer AI pipeline started")
    ensure_directories()

    service = gmail_authenticate()
    unread = get_unread_messages(service)
    logger.info("📥 Unread emails found: %d", len(unread))

    processed_any = False

    for message_ref in unread:
        # Mark as read immediately to prevent reprocessing
        mark_as_read(service, message_ref["id"])

        result = process_email(service, message_ref)
        if not result:
            continue

        final_report, meta = result
        html_report = generate_report(final_report)

        _print_report("AI ANALYSIS RESULT", final_report)

        send_reply(service, meta.sender_email, html_report)
        processed_any = True

    if not processed_any:
        _run_fallback()

    logger.info("✅ Pipeline complete")


def _run_fallback() -> None:
    """Analyse the local fallback test file when no emails matched."""
    if not FALLBACK_FILE.exists():
        logger.warning("❌ No code files found in emails and no fallback file available")
        return

    logger.info("📂 No code attachments found. Falling back to %s", FALLBACK_FILE.name)
    report_text = analyze_file(FALLBACK_FILE)

    if report_text:
        html_report = generate_report(report_text)
        _print_report("AI ANALYSIS RESULT (fallback)", report_text)
    else:
        logger.warning("❌ Fallback file could not be analysed")


# ─── Flask application ──────────────────────────────────────────

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    """Health / base route."""
    return "CodeMailer AI is running 🚀"


@app.route("/run", methods=["GET", "POST"])
def run_pipeline():
    """Trigger the analysis pipeline in a background thread."""
    try:
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        return jsonify({
            "status": "started",
            "message": "CodeMailer AI pipeline is running in background 🚀",
        })
    except Exception as exc:
        logger.error("Failed to start pipeline", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(exc),
        }), 500


@app.route("/health", methods=["GET"])
def health():
    """Liveness check (useful for Cloud Run / k8s)."""
    return "OK", 200


# ─── Entry point ─────────────────────────────────────────────────

if __name__ == "__main__":
    setup_logging()

    config = AppConfig.from_env()
    logger.info("Starting Flask on %s:%d (debug=%s)", config.host, config.port, config.debug)

    app.run(host=config.host, port=config.port, debug=config.debug)