

"""
main.py

This script serves as the main entry point for demonstrating the integration
with the Google Gmail API. It handles user authentication, initializes the
Gmail API service, and utilizes the GmailAPIHandler to fetch and display
user profile, labels, and recent email data.

Logic Breakdown:

1.  OAuth2 Authentication:
    -   Checks for an existing `token.json` file to load saved credentials.
    -   If credentials exist and are valid, it proceeds.
    -   If credentials are expired but a refresh token is available, it attempts
        to refresh the token.
    -   If no valid credentials exist (or refresh fails), it initiates the
        OAuth 2.0 flow, opening a browser for user authentication and saving
        the new token to `token.json` for future use.

2.  Gmail API Service Initialization:
    -   Builds the `googleapiclient.discovery` service object for Gmail API (v1)
        using the obtained credentials.

3.  GmailAPIHandler Usage:
    -   An instance of `GmailAPIHandler` is created, passing the initialized
        Gmail API service.
    -   The `fetch_and_process_gmail_data` asynchronous method is called to
        retrieve a specified number of emails (defaulting to 10), along with
        user profile and label data.

4.  Data Output:
    -   The fetched and processed data (profile, labels, and transformed emails)
        is then printed to the console in a human-readable JSON format.
    -   Email `messageText` is truncated for display if it's very long, to
        keep the output manageable.

5.  Error Handling:
    -   Includes basic `try-except` blocks to catch `HttpError` (for API-specific
        issues) and general `Exception` for unexpected errors, providing
        informative messages.

Usage:
To run this script, ensure you have:
1.  A `credentials.json` file in the same directory, obtained from the Google
    Cloud Console for your project with Gmail API enabled.
2.  All necessary Python libraries installed (`google-api-python-client`,
    `google-auth-oauthlib`, `google-auth-httplib2`).
3.  Execute the script: `python main.py`
"""

import os.path
import asyncio
import json
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from gmail_api_handler import GmailAPIHandler, GMAIL_FIELDS

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]


async def main_async():
    """Shows basic usage of the Gmail API, fetches data, and processes it."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}. Re-authenticating...")
                creds = None

        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0, access_type='offline')

    with open("token.json", "w") as token:
        token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)

        processor = GmailAPIHandler(service) 

        print("Fetching and processing Gmail data from live API...")

        processed_data = await processor.fetch_and_process_gmail_data(num_emails=10)

        print("\n--- Processed User Profile ---")
        print(json.dumps(processed_data['profile'], indent=2))

        print("\n--- Processed Labels ---")
        print(json.dumps(processed_data['labels'], indent=2))

        print("\n--- Processed Emails ---")
        for i, email in enumerate(processed_data['emails']):
            print(f"\n--- Email {i+1} ---")
            for field in GMAIL_FIELDS:
                value = email.get(field)
                if field == "messageText" and value and len(value) > 150:
                    print(f"{field}: {value[:200]}...")
                else:
                    print(f"{field}: {value}")

    except HttpError as error:
        print(f"An HTTP error occurred: {error}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main_async())