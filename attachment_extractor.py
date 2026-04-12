import base64


def extract_attachments(service, message):
    print("📎 Extracting attachments...")

    parts = message["payload"].get("parts", [])

    files = []

    for part in parts:

        filename = part.get("filename")

        if filename:
            print(f"⬇️ Downloading attachment: {filename}")

            attachment_id = part["body"]["attachmentId"]

            attachment = service.users().messages().attachments().get(
                userId="me",
                messageId=message["id"],
                id=attachment_id
            ).execute()

            data = base64.urlsafe_b64decode(
                attachment["data"].encode("UTF-8")
            )

            with open(filename, "wb") as f:
                f.write(data)

            files.append(filename)

            if not files:
                print("⚠️ No attachments found\n")
            else:
                print(f"✅ Extracted {len(files)} file(s)\n")

    return files