"""
AI-powered code analysis via OpenRouter.

Sends code to a configurable LLM endpoint and returns a structured
Markdown review.  Includes retry logic with exponential back-off for
transient network failures.
"""

import logging
import time
from typing import Optional

import httpx

from config import AIConfig

logger = logging.getLogger(__name__)

# ── Analysis prompt template ──────────────────────────────────────
_SYSTEM_PROMPT = (
    "You are a professional Senior Software Engineer and Code Auditor."
)

_USER_PROMPT_TEMPLATE = """\
Analyze the following code snippet.
Provide the response in this exact format:

1. **Language Identification**: Identify the programming language.
2. **Added Comments**: Provide a version of the code with helpful inline comments.
3. **Bug Detection**: List any logic errors, syntax issues, or security risks.
4. **Summary**: A brief overview of what this code does.
5. **Workflow**: Explain the step-by-step logic of the execution.

CODE:
{code}
"""


def analyze_code(code: str, config: Optional[AIConfig] = None) -> str:
    """Send *code* to the AI backend for review.

    Args:
        code: The source code string to analyse.
        config: AI backend configuration.  Defaults to
            :meth:`AIConfig.from_env` when *None*.

    Returns:
        A Markdown-formatted analysis string.  On failure, the string
        starts with ``❌`` so callers can detect errors without
        exceptions.
    """
    if config is None:
        config = AIConfig.from_env()

    if not config.api_key:
        logger.error("❌ OPENROUTER_API_KEY not set in environment")
        return "❌ Error: OPENROUTER_API_KEY not found. Set it in your .env file."

    logger.info("🔑 API key found — calling %s", config.model)

    headers = {
        "Authorization": f"Bearer {config.api_key.strip()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "CodeMailer AI",
    }

    payload = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _USER_PROMPT_TEMPLATE.format(code=code)},
        ],
        "temperature": config.temperature,
    }

    # ── Retry loop with exponential back-off ──────────────────────
    last_error: str = ""
    for attempt in range(1, config.max_retries + 1):
        try:
            with httpx.Client(verify=config.ssl_verify) as client:
                response = client.post(
                    config.api_url,
                    headers=headers,
                    json=payload,
                    timeout=config.timeout_seconds,
                )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]

            last_error = f"HTTP {response.status_code}: {response.text[:200]}"
            logger.warning(
                "⚠️ AI request failed (attempt %d/%d): %s",
                attempt, config.max_retries, last_error,
            )

        except httpx.TimeoutException:
            last_error = "Request timed out"
            logger.warning(
                "⏱️ AI request timed out (attempt %d/%d)",
                attempt, config.max_retries,
            )

        except Exception as exc:
            last_error = str(exc)
            logger.warning(
                "❌ Connection error (attempt %d/%d): %s",
                attempt, config.max_retries, last_error,
            )

        # Back off before retrying (skip sleep on the last attempt)
        if attempt < config.max_retries:
            sleep_time = 2 ** attempt
            logger.debug("💤 Sleeping %ds before retry …", sleep_time)
            time.sleep(sleep_time)

    return f"❌ AI analysis failed after {config.max_retries} attempts. Last error: {last_error}"