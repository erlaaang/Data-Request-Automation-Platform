# mail.py
import re
import requests
from datetime import datetime, timezone

# Default network timeout (seconds) for requests to avoid hanging indefinitely
DEFAULT_TIMEOUT = 10


def extract_request_id(subject):

    if not subject:
        return None

    match = re.search(
        r"\[(.*?)\]",
        subject
    )

    if not match:
        return None

    return match.group(1).upper()


def get_unread_requests(token, mailbox):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    today = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%dT00:00:00Z")

    url = (
    f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages"
    f"?$filter=isRead eq false "
    f"and receivedDateTime ge {today}"
    "&$select=id,subject,conversationId,receivedDateTime,from"
    "&$orderby=receivedDateTime desc"
    "&$top=100"
    )

    print("Checking unread emails...")

    response = requests.get(
        url,
        headers=headers
    )

    response.raise_for_status()

    emails = response.json().get("value", [])

    filtered = []

    for email in emails:

        sender_email = (
            email.get("from", {})
                .get("emailAddress", {})
                .get("address", "")
                .lower()
        )

        subject = email.get("subject", "")

        # Skip bot's own emails
        if sender_email == mailbox.lower():
            continue
        # Skip replies and forwards
        if subject.upper().startswith(("RE:", "FW:")):
            continue
        # Only process request emails
        if not subject.upper().startswith("[AR-"):
            continue
        filtered.append(email)

    print(f"Found {len(filtered)} report requests")

    return filtered



def create_reply_all(
        token,
        mailbox,
        message_id):

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages/{message_id}/createReplyAll",
        headers=headers
    )

    response.raise_for_status()

    return response.json()["id"]


def update_draft(
        token,
        mailbox,
        draft_id,
        share_link,
        request_id):

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = f"""
        <p>Berikut kami lampirkan data sesuai permintaan. Mohon untuk dapat mengelola data sesuai kebutuhan dan melakukan cek ulang pada data yang kami kirim sebelum diserahkan ke pihak terkait. Untuk password file akan kami sampaikan melalui media lain.</p>

        <p><a href="{share_link}">Download Report</a></p>
        <p>Request ID: {request_id}</p>

        <p>Demikian kami sampaikan, atas perhatian dan kerjasamanya kami ucapkan terimakasih.</p>
        
        <p>Best Regards,<br>
        <strong>Erlangga Riyyan Nugraha</strong><br>
        IT Data Management Department<br>
        Technology and Information System Division<br>
        Graha BRI Insurance<br>
        Jl. Mampang Prapatan Raya No.18<br>
        Jakarta Selatan, DKI Jakarta, 12790<br>
        Phone : 021 - 79170477 | Mobile : +628212759155<br>
        <a href="https://www.brins.co.id">www.brins.co.id</a>
        </p>
        """

    response = requests.patch(
        f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages/{draft_id}",
        headers=headers,
        json={
            "body": {
                "contentType": "HTML",
                "content": body
            }
        }
        , timeout=DEFAULT_TIMEOUT
    )

    response.raise_for_status()


def send_draft(
        token,
        mailbox,
        draft_id):

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages/{draft_id}/send",
        headers=headers
    )

    response.raise_for_status()


def mark_as_read(
        token,
        mailbox,
        message_id):

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.patch(
        f"https://graph.microsoft.com/v1.0/users/{mailbox}/messages/{message_id}",
        headers=headers,
        json={
            "isRead": True
        }
        , timeout=DEFAULT_TIMEOUT
    )

    response.raise_for_status()


def reply_all(
        token,
        mailbox,
        message_id,
        share_link,
        request_id):

    draft_id = create_reply_all(
        token,
        mailbox,
        message_id
    )

    update_draft(
        token,
        mailbox,
        draft_id,
        share_link,
        request_id
    )

    send_draft(
        token,
        mailbox,
        draft_id
    )