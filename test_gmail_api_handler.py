"""
Unit tests for the _transform_message_payload method in gmail_api_handler.py.

This test file uses pytest to verify the correct transformation of Gmail API
message payloads into a standardized format. It focuses on the
'_transform_message_payload' method as it's a pure function, allowing for
isolated testing without complex mocking of the Gmail API service or asyncio.

IMPORTANT: These tests reflect the current implementation of _transform_message_payload
which does NOT strip HTML tags or perform advanced text cleaning. Therefore,
assertions for 'messageText' will expect raw HTML content if plain text is not present.

Test Methodology:
- Pytest fixtures are used to set up mock Gmail API message payloads for various scenarios.
- A mock `GmailAPIHandler` instance is provided, but its `service` attribute is `None`
  as `_transform_message_payload` does not interact with the actual API service.
- Each test function focuses on a specific payload structure to ensure granular
  verification of the transformation logic.

Scenarios tested:
1.  **Full Payload:** A 'normal payload' with all expected fields present,
    including both plain text and HTML parts, to ensure correct extraction
    and prioritization of plain text content.
2.  **Missing Optional Fields Payload:** Verifies that the transformation
    handles absent optional data gracefully, assigning `None` or empty lists
    as appropriate (e.g., missing sender, internalDate). `messageText` should
    be extracted from raw HTML if plain text is not available.
3.  **HTML Only Payload:** Specifically tests payloads that contain only HTML
    content (either in a `text/html` part or directly in the main payload body),
    confirming that the raw HTML is correctly extracted as `messageText`.
4.  **No Body Payload:** Assesses payloads where no message body content
    (neither parts nor main payload body data) is present, expecting `messageText` to be `None`.
5.  **Empty Body Payload:** Checks payloads where a text part exists, but its
    decoded content is an empty string, verifying that `messageText` correctly becomes an empty string `""`.
6.  **Attachment Only Payload:** Tests messages that contain only attachments
    (e.g., PDF), with no text or HTML content, ensuring `messageText` is `None`.
7.  **Missing Subject Payload:** Confirms that if the 'Subject' header is
    absent, the `subject` field in the transformed output is correctly `None`.

Fixtures:
- `_b64_encode(text: str)`: A helper to URL-safe base64 encode strings, used for mock body data.
- `mock_gmail_api_handler`: Provides an instance of `GmailAPIHandler` for testing.
- `full_payload`: Represents a typical email with all expected fields.
- `missing_fields_payload`: Simulates an email with some absent optional data.
- `html_only_payload`: A payload consisting solely of HTML content.
- `no_body_payload`: A payload explicitly without any body content.
- `empty_body_payload`: A payload where the body content is an empty string.
- `attachment_only_payload`: A payload containing only file attachments.
- `missing_subject_payload`: A payload missing the 'Subject' header.
"""

import base64
from datetime import datetime
from typing import Any, Dict
import pytest

# Assuming gmail_api_handler is accessible in the test environment
from gmail_api_handler import GmailAPIHandler


def _b64_encode(text: str) -> str:
    """Encodes a string to urlsafe base64."""
    return base64.urlsafe_b64encode(text.encode("utf-8")).decode("utf-8")


@pytest.fixture
def mock_gmail_api_handler():
    """Provides an instance of GmailAPIHandler (service is not used in _transform_message_payload)."""
    return GmailAPIHandler(service=None)


@pytest.fixture
def full_payload() -> Dict[str, Any]:
    """Returns a mock Gmail API message payload with all expected fields."""
    return {
        "id": "full_msg_id_123",
        "threadId": "thread_id_abc",
        "internalDate": "1678886400000",  # March 15, 2023 12:00:00 PM UTC
        "labelIds": ["INBOX", "UNREAD"],
        "payload": {
            "headers": [
                {"name": "From", "value": "Sender Name <sender@example.com>"},
                {"name": "Subject", "value": "Test Subject with Full Fields"},
                {"name": "Date", "value": "Wed, 15 Mar 2023 12:00:00 +0000"},
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": _b64_encode("This is the plain text content.")},
                },
                {
                    "mimeType": "text/html",
                    "body": {"data": _b64_encode("<html><body><p>This is <b>HTML</b> content.</p></body></html>")},
                },
            ],
        },
    }


@pytest.fixture
def missing_fields_payload() -> Dict[str, Any]:
    """Returns a mock Gmail API message payload with some optional fields missing."""
    return {
        "id": "missing_msg_id_456",
        "threadId": "thread_id_def",       
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test Subject - Missing Fields"},
            ],
            "parts": [
                {
                    "mimeType": "text/html",
                    "body": {"data": _b64_encode("<html><body><p>Only HTML here.</p></body></html>")},
                },
            ],
        },
    }


@pytest.fixture
def html_only_payload() -> Dict[str, Any]:
    """Returns a mock Gmail API message payload with only HTML content
    directly in the payload body (no parts), simulating a simple HTML email.
    """
    return {
        "id": "html_only_msg_789",
        "threadId": "thread_id_ghi",
        "internalDate": "1678886400000",
        "labelIds": ["SENT"],
        "payload": {
            "headers": [
                {"name": "From", "value": "HTML Sender <html@example.com>"},
                {"name": "Subject", "value": "HTML Only Email"},
            ],
            "body": {"data": _b64_encode("<html><body><h1>Hello!</h1><p>This is a <b>simple</b> HTML email.</p></body></html>")},
            "mimeType": "text/html"
        },
    }


@pytest.fixture
def no_body_payload() -> Dict[str, Any]:
    """Returns a mock Gmail API message payload with no body data at all."""
    return {
        "id": "no_body_msg_101",
        "threadId": "thread_id_jkl",
        "internalDate": "1678886400000",
        "labelIds": ["INBOX"],
        "payload": {
            "headers": [
                {"name": "From", "value": "No Body <nobody@example.com>"},
                {"name": "Subject", "value": "Email with No Body"},
            ],
        },
    }

@pytest.fixture
def empty_body_payload() -> Dict[str, Any]:
    """Returns a mock Gmail API message payload with empty string body data."""
    return {
        "id": "empty_body_msg_102",
        "threadId": "thread_id_mno",
        "internalDate": "1678886400000",
        "labelIds": ["SENT"],
        "payload": {
            "headers": [
                {"name": "From", "value": "Empty Body <empty@example.com>"},
                {"name": "Subject", "value": "Email with Empty Body"},
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": _b64_encode("")},
                },
            ],
        },
    }

@pytest.fixture
def attachment_only_payload() -> Dict[str, Any]:
    """Returns a mock Gmail API message payload with only an attachment part."""
    return {
        "id": "attach_only_msg_103",
        "threadId": "thread_id_pqr",
        "internalDate": "1678886400000",
        "labelIds": ["INBOX"],
        "payload": {
            "headers": [
                {"name": "From", "value": "Attachment Sender <attach@example.com>"},
                {"name": "Subject", "value": "Email with Attachment Only"},
            ],
            "parts": [
                {
                    "mimeType": "application/pdf",
                    "filename": "document.pdf",
                    "body": {"attachmentId": "some_id", "size": 12345},
                },
            ],
        },
    }

@pytest.fixture
def missing_subject_payload() -> Dict[str, Any]:
    """Returns a mock Gmail API message payload with the 'Subject' header missing."""
    return {
        "id": "no_subj_msg_104",
        "threadId": "thread_id_stu",
        "internalDate": "1678886400000",
        "labelIds": ["INBOX"],
        "payload": {
            "headers": [
                {"name": "From", "value": "No Subject <nosubj@example.com>"},
            ],
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": _b64_encode("This email has no subject.")},
                },
            ],
        },
    }


def test_transform_message_payload_full_fields(
    mock_gmail_api_handler: GmailAPIHandler, full_payload: Dict[str, Any]
) -> None:
    """
    Tests _transform_message_payload with a full payload including plain text.
    Verifies all fields are correctly extracted and messageText prioritizes plain.
    """
    transformed = mock_gmail_api_handler._transform_message_payload(full_payload)

    assert transformed["messageId"] == "full_msg_id_123"
    assert transformed["threadId"] == "thread_id_abc"
    assert transformed["labelIds"] == ["INBOX", "UNREAD"]
    assert transformed["sender"] == "Sender Name <sender@example.com>"
    assert transformed["subject"] == "Test Subject with Full Fields"
    
    expected_timestamp = datetime.fromtimestamp(1678886400000 / 1000).isoformat()
    assert transformed["messageTimestamp"] == expected_timestamp
    
    assert transformed["messageText"] == "This is the plain text content."


def test_transform_message_payload_missing_fields(
    mock_gmail_api_handler: GmailAPIHandler, missing_fields_payload: Dict[str, Any]
) -> None:
    """
    Tests _transform_message_payload with a payload missing optional fields.
    Verifies that missing fields are handled gracefully (None or empty list).
    messageText should be extracted from raw HTML as no cleaning is applied.
    """
    transformed = mock_gmail_api_handler._transform_message_payload(
        missing_fields_payload
    )

    assert transformed["messageId"] == "missing_msg_id_456"
    assert transformed["threadId"] == "thread_id_def"
    assert transformed["labelIds"] == []
    assert transformed["sender"] is None 
    assert transformed["subject"] == "Test Subject - Missing Fields"
    assert transformed["messageTimestamp"] is None
    
    assert transformed["messageText"] == "<html><body><p>Only HTML here.</p></body></html>"


def test_transform_message_payload_html_only(
    mock_gmail_api_handler: GmailAPIHandler, html_only_payload: Dict[str, Any]
) -> None:
    """
    Tests _transform_message_payload with a payload that only has HTML content
    directly in the payload body (no parts).
    Verifies raw HTML is extracted as messageText.
    """
    transformed = mock_gmail_api_handler._transform_message_payload(html_only_payload)

    assert transformed["messageId"] == "html_only_msg_789"
    assert transformed["threadId"] == "thread_id_ghi"
    assert transformed["labelIds"] == ["SENT"]
    assert transformed["sender"] == "HTML Sender <html@example.com>"
    assert transformed["subject"] == "HTML Only Email"

    expected_timestamp = datetime.fromtimestamp(1678886400000 / 1000).isoformat()
    assert transformed["messageTimestamp"] == expected_timestamp
    
    assert transformed["messageText"] == "<html><body><h1>Hello!</h1><p>This is a <b>simple</b> HTML email.</p></body></html>"


def test_transform_message_payload_no_body(
    mock_gmail_api_handler: GmailAPIHandler, no_body_payload: Dict[str, Any]
) -> None:
    """
    Tests _transform_message_payload with a payload that has no body content (no parts, no body data).
    messageText should be None.
    """
    transformed = mock_gmail_api_handler._transform_message_payload(no_body_payload)

    assert transformed["messageId"] == "no_body_msg_101"
    assert transformed["threadId"] == "thread_id_jkl"
    assert transformed["sender"] == "No Body <nobody@example.com>"
    assert transformed["subject"] == "Email with No Body"
    assert transformed["messageText"] is None


def test_transform_message_payload_empty_body(
    mock_gmail_api_handler: GmailAPIHandler, empty_body_payload: Dict[str, Any]
) -> None:
    """
    Tests _transform_message_payload with a payload where the body data is an empty string.
    messageText should be an empty string.
    """
    transformed = mock_gmail_api_handler._transform_message_payload(empty_body_payload)

    assert transformed["messageId"] == "empty_body_msg_102"
    assert transformed["threadId"] == "thread_id_mno"
    assert transformed["sender"] == "Empty Body <empty@example.com>"
    assert transformed["subject"] == "Email with Empty Body"
    assert transformed["messageText"] == ""


def test_transform_message_payload_attachment_only(
    mock_gmail_api_handler: GmailAPIHandler, attachment_only_payload: Dict[str, Any]
) -> None:
    """
    Tests _transform_message_payload with a payload that only has attachment parts
    and no text/html parts. messageText should be None.
    """
    transformed = mock_gmail_api_handler._transform_message_payload(attachment_only_payload)

    assert transformed["messageId"] == "attach_only_msg_103"
    assert transformed["threadId"] == "thread_id_pqr"
    assert transformed["sender"] == "Attachment Sender <attach@example.com>"
    assert transformed["subject"] == "Email with Attachment Only"
    assert transformed["messageText"] is None


def test_transform_message_payload_missing_subject(
    mock_gmail_api_handler: GmailAPIHandler, missing_subject_payload: Dict[str, Any]
) -> None:
    """
    Tests _transform_message_payload with a payload where the 'Subject' header is missing.
    Subject should be None.
    """
    transformed = mock_gmail_api_handler._transform_message_payload(missing_subject_payload)

    assert transformed["messageId"] == "no_subj_msg_104"
    assert transformed["threadId"] == "thread_id_stu"
    assert transformed["sender"] == "No Subject <nosubj@example.com>"
    assert transformed["subject"] is None
    assert transformed["messageText"] == "This email has no subject."