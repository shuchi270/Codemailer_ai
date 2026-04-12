from gmail_auth import gmail_authenticate

def get_unread_emails():

    service = gmail_authenticate()

    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        q="is:unread"
    ).execute()

    messages = results.get("messages", [])

    return messages


# ----TESTING----
# emails = get_unread_emails()
# print(emails)

def get_email_content(service, msg_id):

    message = service.users().messages().get(
        userId="me",
        id=msg_id
    ).execute()

    return message


# emails = get_unread_emails()
# print(emails)
# if emails:
#     service = gmail_authenticate()
#     for email in emails:
#         content = get_email_content(service, email["id"])
#print(content)