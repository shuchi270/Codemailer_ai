from pathlib import Path

from dotenv import load_dotenv
from pygments.lexers import guess_lexer_for_filename

from ai_analyzer import analyze_code
from attachment_extractor import extract_attachments
from gmail_auth import gmail_authenticate
from gmail_reader import get_email_content
from gmail_sender import send_reply
from report_generator import generate_report

load_dotenv()

BASE_DIR = Path(__file__).parent
FALLBACK_FILE = BASE_DIR / "test.py"
TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go",
    ".rb", ".php", ".rs", ".swift", ".kt", ".scala", ".html",
    ".css", ".json", ".xml", ".yaml", ".yml", ".sql", ".sh",
}


def get_unread_messages(service):
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        q="is:unread"
    ).execute()
    return results.get("messages", [])


def read_text_file(file_path):
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def looks_like_code(file_path, code):
    if file_path.suffix.lower() in TEXT_EXTENSIONS:
        return True

    try:
        guess_lexer_for_filename(file_path.name, code)
        return True
    except Exception:
        return False


def analyze_file(file_path):
    code = read_text_file(file_path)
    if not code:
        return None

    if not looks_like_code(file_path, code):
        return None

    print(f"🤖 Analyzing {file_path.name}...")

    try:
        lexer = guess_lexer_for_filename(file_path.name, code)
        language_line = f"Detected language: {lexer.name}\n\n"
    except Exception:
        language_line = ""

    analysis = analyze_code(code)
    return f"# File: {file_path.name}\n\n{language_line}{analysis}"


def process_email(service, message_ref):
    message = get_email_content(service, message_ref["id"])
    headers = message.get("payload", {}).get("headers", [])
    header_map = {header["name"]: header["value"] for header in headers}

    print(f"📧 Processing email: {header_map.get('Subject', '(No Subject)')}")

    downloaded_files = extract_attachments(service, message)
    analyses = []

    for filename in downloaded_files:
        file_path = BASE_DIR / filename
        if not file_path.exists():
            continue

        analysis = analyze_file(file_path)
        if analysis:
            analyses.append(analysis)

    if not analyses:
        return None

    email_summary = [
        f"### Email Details",
        f"**Subject:** {header_map.get('Subject', '(No Subject)')}",
        f"**From:** {header_map.get('From', 'Unknown Sender')}",
        f"**Message ID:** {message.get('id', 'N/A')}",
        "---",
    ]
    return "\n".join(email_summary) + "\n\n".join(analyses), header_map.get('From')


def process_fallback_file():
    if not FALLBACK_FILE.exists():
        return None

    print(f"📂 No code attachments found. Falling back to {FALLBACK_FILE.name}.")
    return analyze_file(FALLBACK_FILE)


def main():
    print("🚀 CodeMailer AI started successfully!")

    service = gmail_authenticate()
    unread_messages = get_unread_messages(service)

    print(f"📥 Unread emails found: {len(unread_messages)}")

    final_report = None
    sender_email = None

    for message_ref in unread_messages:
        result = process_email(service, message_ref)
        if result:
            final_report, sender_email = result
            break

    if not final_report:
        final_report = process_fallback_file()

    if not final_report:
        print("❌ No readable code files were found in unread emails or the fallback test file.")
        return

    html_report = generate_report(final_report)

    print("\n" + "=" * 50)
    print("AI ANALYSIS RESULT:")
    print("=" * 50)
    print(final_report)
    print("=" * 50)
    print("Report generated: report.html")
    print("=" * 50)

    if sender_email:
        import re
        match = re.search(r'<([^>]+)>', sender_email)
        to_email = match.group(1) if match else sender_email
        send_reply(service, to_email, html_report)


if __name__ == "__main__":
    main()
