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

for email in emails:
    print(email["subject"])
    print(email["id"])
    print("-" * 50)