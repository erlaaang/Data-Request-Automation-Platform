import configparser

from modules.auth import get_token
from modules.mail import get_unread_requests, reply_all

config = configparser.ConfigParser()
config.read("config.ini")

token = get_token(config)

emails = get_unread_requests(
    token,
    config["graph"]["mailbox"]
)

mailbox = config["graph"]["mailbox"]
message_id = emails[0]["id"]

print("Found emails:")

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
