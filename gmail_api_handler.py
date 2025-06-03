"""
gmail_api_handler.py

This module provides the GmailAPIHandler class, designed to interact with the
Google Gmail API to fetch user data and process email messages. It abstracts
away the complexities of API calls, asynchronous execution, and data
transformation into a standardized format.

Key Features:
- Asynchronous API calls using `asyncio.to_thread` to prevent blocking the event loop.
- Concurrency control for fetching individual message details using `asyncio.Semaphore`.
- Robust transformation of raw Gmail API message payloads into a simplified,
  consistent dictionary structure.

Detailed Logic:

GmailAPIHandler Class:
- __init__(self, service, concurrent_requests_limit: int = 1):
    Initializes the handler with an authenticated Gmail API service object
    and an optional limit for concurrent message detail fetches.

- async fetch_and_process_gmail_data(self, num_emails: int = 10) -> Dict[str, Any]:
    An asynchronous method to orchestrate the fetching of Gmail data.
    1. Fetches user profile, labels, and a list of message IDs concurrently.
    2. If messages are found, it then fetches the full details for each message
       concurrently, respecting the `concurrent_requests_limit`.
    3. Each full message payload is then passed to `_transform_message_payload`
       for standardization.
    4. Returns a dictionary containing profile, labels, and the list of
       transformed emails.
    5. Includes robust error handling and logging for API interactions.

- _transform_message_payload(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
    A private helper method responsible for taking a raw Gmail API message
    payload and transforming it into a structured dictionary. This method
    is pure and does not perform API calls.

    Transformed Fields:
    - "messageId" (str): The unique ID of the email message.
    - "threadId" (str): The ID of the conversation thread the message belongs to.
    - "messageTimestamp" (str, Optional): The internal creation date of the
      message in ISO 8601 format. None if internalDate is missing.
    - "labelIds" (List[str]): A list of label IDs applied to the message (e.g., INBOX, UNREAD, SENT).
      Defaults to an empty list if not present.
    - "sender" (str, Optional): The 'From' header value (e.g., "Sender Name <email@example.com>").
      None if the header is missing.
    - "subject" (str, Optional): The 'Subject' header value of the email.
      None if the header is missing.
    - "messageText" (str, Optional): The body content of the email.
      The extraction logic prioritizes content in the following order:
      1.  `text/plain` part: If a 'text/plain' MIME part is found and has data,
          its decoded content is used.
      2.  `text/html` part: If no 'text/plain' part is found, it falls back
          to the first `text/html` MIME part found.
      3.  Main `payload.body`: If no suitable parts are found, it checks if
          the main `payload['body']` contains data (e.g., for simple HTML emails
          without explicit parts).
      IMPORTANT: This method does NOT strip HTML tags. If HTML content is extracted,
      it will be returned as raw HTML. An empty string "" is returned if a content
      part exists but its decoded data is empty. None is returned if no suitable
      text/html content is found at all.

Dependencies:
- asyncio: For asynchronous operations and concurrency.
- base64: For decoding message body data from URL-safe base64.
- logging: For operational logs.
- datetime: For timestamp conversion.
"""


import asyncio
import base64
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GMAIL_FIELDS = [
    "messageId",
    "threadId",
    "messageTimestamp",
    "labelIds",
    "sender",
    "subject",
    "messageText",
]


class GmailAPIHandler:
    def __init__(self, service, concurrent_requests_limit: int = 1):
        self.service = service
        self.semaphore = asyncio.Semaphore(concurrent_requests_limit)

    async def fetch_and_process_gmail_data(self, num_emails: int = 10) -> Dict[str, Any]:
        try:
            profile_request = self.service.users().getProfile(userId='me')
            labels_request = self.service.users().labels().list(userId='me')
            messages_list_request = self.service.users().messages().list(userId='me', maxResults=num_emails)

            profile_task = asyncio.to_thread(profile_request.execute)
            labels_task = asyncio.to_thread(labels_request.execute)
            messages_list_task = asyncio.to_thread(messages_list_request.execute)

            profile_result, labels_response, messages_list_response = await asyncio.gather(profile_task, labels_task, messages_list_task)
            
            profile = profile_result
            labels = labels_response.get('labels', [])
            messages_list = messages_list_response.get('messages', [])
            
            logger.info("Fetched profile, labels, and message list.")

            processed_emails = []
            if messages_list:
                message_detail_tasks = []
                for msg_summary in messages_list:
                    async def fetch_message_with_semaphore(msg_id):
                        async with self.semaphore:
                            get_message_request = self.service.users().messages().get(userId='me', id=msg_id, format='full')
                            return await asyncio.to_thread(get_message_request.execute)

                    message_detail_tasks.append(fetch_message_with_semaphore(msg_summary['id']))

                full_messages = await asyncio.gather(*message_detail_tasks)
                logger.info(f"Fetched full details for {len(full_messages)} messages.")

                processed_emails = [
                    self._transform_message_payload(msg_data) for msg_data in full_messages
                ]
                logger.info("All messages transformed.")

            return {
                "profile": profile,
                "labels": labels,
                "emails": processed_emails
            }

        except Exception as e:
            logger.error(f"An unexpected error occurred during fetch_and_process_gmail_data: {e}")
            raise

    def _transform_message_payload(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        transformed = {
            "messageId": message_data.get("id"),
            "threadId": message_data.get("threadId"),
            "labelIds": message_data.get("labelIds", []),
        }

        headers = message_data.get("payload", {}).get("headers", [])
        header_map = {h["name"].lower(): h["value"] for h in headers}

        transformed["sender"] = header_map.get("from")
        transformed["subject"] = header_map.get("subject")

        internal_date_ms = message_data.get("internalDate")
        if internal_date_ms:
            transformed["messageTimestamp"] = datetime.fromtimestamp(int(internal_date_ms) / 1000).isoformat()
        else:
            transformed["messageTimestamp"] = None

        payload = message_data.get("payload", {})
        parts = payload.get("parts", [])

        plain_text_content: Optional[str] = None
        html_content: Optional[str] = None
        main_payload_body_content: Optional[str] = None

        for part in parts:
            body_data = part.get("body", {}).get("data")
            if part.get("mimeType") == "text/plain" and body_data is not None:
                plain_text_content = base64.urlsafe_b64decode(body_data).decode("utf-8")
                break

        if plain_text_content is None:
            for part in parts:
                body_data = part.get("body", {}).get("data")
                if part.get("mimeType") == "text/html" and body_data is not None:
                    html_content = base64.urlsafe_b64decode(body_data).decode("utf-8")
                    break

        if plain_text_content is None and html_content is None:
            main_body_data = payload.get("body", {}).get("data")
            if main_body_data is not None:
                if payload.get("mimeType") == "text/html":
                    main_payload_body_content = base64.urlsafe_b64decode(main_body_data).decode("utf-8")
                elif payload.get("mimeType") == "text/plain":
                    main_payload_body_content = base64.urlsafe_b64decode(main_body_data).decode("utf-8")
                else:
                    main_payload_body_content = base64.urlsafe_b64decode(main_body_data).decode("utf-8")

        if plain_text_content is not None:
            transformed["messageText"] = plain_text_content
        elif html_content is not None:
            transformed["messageText"] = html_content
        elif main_payload_body_content is not None:
            transformed["messageText"] = main_payload_body_content
        else:
            transformed["messageText"] = None

        return transformed