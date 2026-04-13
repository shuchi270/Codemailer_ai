# 🚀 CodeMailer AI

CodeMailer AI is an end-to-end Python automation tool that turns your Gmail inbox into a seamless, AI-powered **Code Reviewer**. It automatically detects unread emails containing code files, analyzes them using advanced AI models via OpenRouter (such as Gemini 2.0 Flash), generates a beautifully formatted, syntax-highlighted HTML report, and replies directly to the original sender.

## ✨ Features

- **Automated Gmail Integration**: Uses OAuth 2.0 with **token caching** to securely access your inbox, fetch unread messages, and extract code-file attachments.
- **Deep AI Code Analysis**: Uses cutting-edge LLMs via OpenRouter to produce structured code reviews:
  1. Language identification
  2. Code with inline explanatory comments
  3. Bug detection (logic errors, syntax issues, security risks)
  4. Concise summary
  5. Step-by-step execution workflow
- **Retry with Backoff**: Transient network failures are automatically retried with exponential back-off.
- **Stunning HTML Reports**: Markdown analysis rendered with Pygments syntax highlighting in a modern dark-mode HTML template.
- **Auto-Reply Workflow**: Automatically sends the generated report back to the original sender.
- **Local Fallback Mode**: No relevant emails? The system falls back to analyzing the local `test.py` file.

## 🛠️ Project Structure

| File | Purpose |
|---|---|
| `main.py` | Flask server + pipeline orchestrator |
| `config.py` | Centralized configuration, constants, and logging setup |
| `gmail_auth.py` | OAuth 2.0 authentication with **token caching** |
| `gmail_reader.py` | Fetch unread emails, read content, mark as read |
| `attachment_extractor.py` | Download & manage code-file attachments |
| `ai_analyzer.py` | OpenRouter API interaction with retry logic |
| `report_generator.py` | Markdown → HTML report generation |
| `gmail_sender.py` | Compose and send HTML email replies |
| `templates/report.html` | Jinja2 HTML report template |
| `test.py` | Sample code for fallback analysis mode |

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configuration

1. Place your Google OAuth `credentials.json` in the project root.
2. Create a `.env` file:

```env
OPENROUTER_API_KEY=sk-or-v1-...

# Optional overrides:
# AI_MODEL=google/gemini-2.0-flash-001
# AI_TIMEOUT=45
# AI_MAX_RETRIES=3
# SSL_VERIFY=true
# DEBUG=false
# PORT=8080
```

### 3. Run

```bash
python3 main.py
```

1. On **first run**, a browser window opens for Google OAuth consent. Credentials are cached in `token.json` for subsequent runs.
2. The Flask server starts on port 8080 (or `$PORT`).
3. Hit `GET /run` to trigger the pipeline:
   - Scans inbox for unread emails
   - Downloads & analyzes code attachments
   - Generates an HTML report (saved to `reports/`)
   - Replies to the sender with the report

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health / base route |
| `/run` | GET, POST | Trigger the analysis pipeline (background) |
| `/health` | GET | Liveness check (Cloud Run / k8s) |

## 🔧 Troubleshooting

| Problem | Fix |
|---|---|
| `OPENROUTER_API_KEY not found` | Ensure `.env` file exists in project root with the key set |
| SSL errors on macOS | Set `SSL_VERIFY=false` in `.env` (development only) |
| `credentials.json` not found | Download OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |
| Token expired / revoked | Delete `token.json` and re-run to re-authenticate |

## 🤝 Contributing

Contributions are welcome! Please ensure changes are well-documented and follow the established patterns (type hints, docstrings, logging via the `logging` module).

---

*CodeMailer AI — automated code review, straight from your inbox.*
