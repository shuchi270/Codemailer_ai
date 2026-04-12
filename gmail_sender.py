from email.mime.text import MIMEText
import base64


def send_reply(service, to_email, html_report):
    print("📤 Sending reply email...")

    message = MIMEText(html_report, "html")

    message["to"] = to_email
    message["subject"] = "Code Analysis Report"

    raw = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    body = {"raw": raw}

    service.users().messages().send(
        userId="me",
        body=body
    ).execute()

    print("✅ Reply sent successfully!\n")