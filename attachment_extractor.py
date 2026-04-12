import base64


def get_all_parts(parts):
    all_parts = []
    for part in parts:
        all_parts.append(part)
        if "parts" in part:
            all_parts.extend(get_all_parts(part["parts"]))
    return all_parts

def extract_attachments(service, message):
    print("📎 Extracting attachments...")

    payload = message.get("payload", {})
    parts = []
    if "parts" in payload:
        parts = get_all_parts(payload["parts"])
    else:
        parts = [payload]

    files = []

    for part in parts:
        filename = part.get("filename")

        if filename:
            print(f"⬇️ Downloading attachment: {filename}")

            attachment_id = part["body"].get("attachmentId")
            
            if attachment_id:
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