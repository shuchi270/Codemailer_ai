"""
HTML report generator.

Converts Markdown analysis text into a styled HTML report using a
Jinja2 template and Pygments syntax highlighting.
"""

import logging
from datetime import datetime
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader

from config import REPORTS_DIR, TEMPLATES_DIR

logger = logging.getLogger(__name__)


def generate_report(analysis: str) -> str:
    """Render an analysis string into a styled HTML report.

    The report is rendered from the Jinja2 template at
    ``templates/report.html`` and saved into the ``reports/``
    directory with a timestamped filename.

    Args:
        analysis: Markdown-formatted analysis text.

    Returns:
        The rendered HTML string (also used as the email body).
    """
    REPORTS_DIR.mkdir(exist_ok=True)

    # ── Markdown → HTML with syntax highlighting ──────────────────
    html_analysis = markdown.markdown(
        analysis,
        extensions=["fenced_code", "codehilite"],
        extension_configs={
            "codehilite": {
                "noclasses": True,
                "pygments_style": "monokai",
            }
        },
    )

    # ── Render Jinja2 template ────────────────────────────────────
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report.html")
    html = template.render(analysis=html_analysis)

    # ── Save to reports/ directory ────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORTS_DIR / f"report_{timestamp}.html"
    report_path.write_text(html, encoding="utf-8")

    logger.info("📄 Report saved: %s", report_path.name)
    return html