from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def gmail_authenticate():

    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES
    )

    creds = flow.run_local_server(port=0)

    service = build("gmail", "v1", credentials=creds)

    return service

if __name__ == "__main__":
    service = gmail_authenticate()
    print("Gmail authentication successful!")