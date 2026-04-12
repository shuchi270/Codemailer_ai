# 🚀 CodeMailer AI

CodeMailer AI is an end-to-end Python automation tool that turns your Gmail inbox into a seamless, AI-powered Code Reviewer. It automatically detects unread emails containing code files, analyzes them using advanced AI models via OpenRouter (such as Gemini 2.0 Flash), generates a beautifully formatted, syntax-highlighted HTML report, and replies directly to the original sender.

## ✨ Features

- **Automated Gmail Integration**: Uses OAuth 2.0 to securely access your inbox, fetch unread messages, and extract Python (`.py`) attachments.
- **Deep AI Code Analysis**: Uses cutting-edge AI models to provide deeply structured code reviews. By default, it returns:
  1. Language identification
  2. The original code formatted with inline explanatory comments added
  3. Detailed bug detection (logic errors, syntax issues, etc.)
  4. A succinct overall summary
  5. A step-by-step workflow of how the code executes
- **Stunning HTML Reports**: Markdown analysis is dynamically parsed and combined with Pygments syntax highlighting. The report is delivered in a premium, modern dark-mode HTML template with clear, high-contrast, pure-black snippet rendering and single-tone elegant comment typography.
- **Auto-Reply Workflow**: Automatically sends the generated rich-text HTML report back to the original sender's email address.
- **Local Fallback Mode**: If no relevant emails are found in your inbox, it organically falls back to scanning and analyzing local test files.

## 🛠️ Project Structure

- `main.py` - The main entry point that drives the automation pipeline.
- `gmail_auth.py` - Handles secure OAuth 2.0 authentication with Gmail.
- `gmail_reader.py` - Fetches unread emails and safely reads metadata.
- `attachment_extractor.py` - Downloads and extracts attached code files dynamically.
- `ai_analyzer.py` - Manages the OpenRouter API interaction and structures the code review prompt.
- `report_generator.py` - Translates Markdown to structured HTML and parses code blocks via Pygments.
- `templates/report.html` - The stylish, responsive Jinja2 HTML template.
- `gmail_sender.py` - Composes the final HTML payload and automatically sends the finalized Code Review directly to the user.
- `.env` - Environment variables (contains your `OPENROUTER_API_KEY`).

## 🚀 Getting Started

### 1. Requirements

Install all necessary dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration

Make sure your Google OAuth credentials (`credentials.json`) are present in the project's root folder.

Create a `.env` file containing your OpenRouter API Key:
```env
OPENROUTER_API_KEY=sk-or-v1-...
```

### 3. Usage

Run the main application:
```bash
python3 main.py
```

1. You will be prompted to authenticate with your Google Account in the browser (if not already authenticated).
2. The script will automatically scan your `INBOX` for unread emails.
3. If attachments are found, they will be downloaded, parsed, styled, and evaluated.
4. The parsed HTML analysis payload is securely generated locally (`report.html`) and emailed securely back to the sender.

## 🤝 Contributing

Contributions are welcome! Please ensure any robust structural enhancements or feature additions are well-documented.

---

*CodeMailer AI is entirely operational and optimized!*
