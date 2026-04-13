"""
Centralized configuration for CodeMailer AI.

All constants, paths, environment variables, and language mappings
live here — imported by every other module.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Set

from dotenv import load_dotenv

# ── Load environment once ─────────────────────────────────────────
BASE_DIR = Path(__file__).parent
_env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=_env_path, override=True)


# ── Directories ───────────────────────────────────────────────────
ATTACHMENTS_DIR = BASE_DIR / "attachments"
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "templates"
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"
FALLBACK_FILE = BASE_DIR / "test.py"


# ── Supported code file extensions ────────────────────────────────
TEXT_EXTENSIONS: Set[str] = {
    ".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go",
    ".rb", ".php", ".rs", ".swift", ".kt", ".scala", ".html",
    ".css", ".json", ".xml", ".yaml", ".yml", ".sql", ".sh",
}

# ── Extension → human-readable language name ─────────────────────
LANGUAGE_MAP: Dict[str, str] = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".java": "Java", ".cpp": "C++", ".c": "C", ".cs": "C#",
    ".go": "Go", ".rb": "Ruby", ".php": "PHP", ".rs": "Rust",
    ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala",
    ".html": "HTML", ".css": "CSS", ".json": "JSON",
    ".xml": "XML", ".yaml": "YAML", ".yml": "YAML",
    ".sql": "SQL", ".sh": "Shell Script",
}

# ── Gmail OAuth scopes ────────────────────────────────────────────
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


@dataclass(frozen=True)
class AIConfig:
    """Configuration for the OpenRouter AI backend."""

    api_key: str = ""
    api_url: str = "https://openrouter.ai/api/v1/chat/completions"
    model: str = "google/gemini-2.0-flash-001"
    temperature: float = 0.3
    timeout_seconds: float = 45.0
    ssl_verify: bool = True
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> "AIConfig":
        """Build config from environment variables."""
        return cls(
            api_key=os.getenv("OPENROUTER_API_KEY", ""),
            api_url=os.getenv("AI_API_URL", cls.api_url),
            model=os.getenv("AI_MODEL", cls.model),
            temperature=float(os.getenv("AI_TEMPERATURE", str(cls.temperature))),
            timeout_seconds=float(os.getenv("AI_TIMEOUT", str(cls.timeout_seconds))),
            ssl_verify=os.getenv("SSL_VERIFY", "true").lower() in ("true", "1", "yes"),
            max_retries=int(os.getenv("AI_MAX_RETRIES", str(cls.max_retries))),
        )


@dataclass(frozen=True)
class AppConfig:
    """Top-level application configuration."""

    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    ai: AIConfig = field(default_factory=AIConfig.from_env)

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            host=os.getenv("HOST", cls.host),
            port=int(os.getenv("PORT", str(cls.port))),
            debug=os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
            ai=AIConfig.from_env(),
        )


def ensure_directories() -> None:
    """Create required output directories if they don't exist."""
    ATTACHMENTS_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure the root logger with a consistent format."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Quiet noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient").setLevel(logging.WARNING)
    logging.getLogger("google_auth_httplib2").setLevel(logging.WARNING)
