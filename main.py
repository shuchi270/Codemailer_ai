import os
import threading
from pathlib import Path

from dotenv import load_dotenv
from pygments.lexers import guess_lexer_for_filename
from flask import Flask, jsonify

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
        q="is:unread",
        maxResults=1
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


def get_language_name(file_path, code):
    mapping = {
        ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", 
        ".java": "Java", ".cpp": "C++", ".c": "C", ".cs": "C#", 
        ".go": "Go", ".rb": "Ruby", ".php": "PHP", ".rs": "Rust", 
        ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala", 
        ".html": "HTML", ".css": "CSS", ".json": "JSON", 
        ".xml": "XML", ".yaml": "YAML", ".yml": "YAML", 
        ".sql": "SQL", ".sh": "Shell Script"
    }
    ext = file_path.suffix.lower()
    if ext in mapping:
        return mapping[ext]
    try:
        lexer = guess_lexer_for_filename(file_path.name, code)
        return lexer.name
    except Exception:
        return "Unknown"

def analyze_file(file_path):
    code = read_text_file(file_path)
    if not code:
        return None

    if not looks_like_code(file_path, code):
        return None

    print(f"🤖 Analyzing {file_path.name}...")

    lang_name = get_language_name(file_path, code)
    if lang_name != "Unknown":
        language_line = f"Detected language: {lang_name}\n\n"
    else:
        language_line = ""

    analysis = analyze_code(code)
    return f"# File: {file_path.name}\n\n{language_line}{analysis}"


def process_email(service, message_ref):
    message = get_email_content(service, message_ref["id"])
    headers = message.get("payload", {}).get("headers", [])
    header_map = {header["name"].lower(): header["value"] for header in headers}

    print(f"📧 Processing email: {header_map.get('subject', '(No Subject)')}")

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
        f"**Subject:** {header_map.get('subject', '(No Subject)')}",
        f"**From:** {header_map.get('from', 'Unknown Sender')}",
        f"**Message ID:** {message.get('id', 'N/A')}",
        "---",
    ]
    return "\n".join(email_summary) + "\n\n".join(analyses), header_map.get('from')


def process_fallback_file():
    if not FALLBACK_FILE.exists():
        return None

    print(f"📂 No code attachments found. Falling back to {FALLBACK_FILE.name}.")
    return analyze_file(FALLBACK_FILE)


def run():
    print("🚀 CodeMailer AI started successfully!")

    service = gmail_authenticate()
    unread_messages = get_unread_messages(service)

    print(f"📥 Unread emails found: {len(unread_messages)}")

    processed_any = False

    for message_ref in unread_messages:
        result = process_email(service, message_ref)
        
        # Mark as read to avoid processing the same email infinitely
        try:
            service.users().messages().modify(
                userId="me",
                id=message_ref["id"],
                body={"removeLabelIds": ["UNREAD"]}
            ).execute()
        except Exception as e:
            pass
            
        if result:
            final_report, sender_email = result
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
            
            processed_any = True

    if not processed_any:
        final_report = process_fallback_file()
        if final_report:
            html_report = generate_report(final_report)

            print("\n" + "=" * 50)
            print("AI ANALYSIS RESULT:")
            print("=" * 50)
            print(final_report)
            print("=" * 50)
            print("Report generated: report.html")
            print("=" * 50)
        else:
            print("❌ No readable code files were found in unread emails or the fallback test file.")


app = Flask(__name__)

# ✅ Health / base route
@app.route("/", methods=["GET"])
def home():
    return "CodeMailer AI is running 🚀"

# ✅ Run pipeline in background thread
@app.route("/run", methods=["GET", "POST"])
def run_pipeline():
    try:
        thread = threading.Thread(target=run)
        thread.start()
        return jsonify({
            "status": "started",
            "message": "CodeMailer AI pipeline is running in background 🚀"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# ✅ Optional: health check endpoint (good for Cloud Run)
@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        debug=True
    )