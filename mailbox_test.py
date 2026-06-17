import configparser
import requests

from modules.auth import get_token

config = configparser.ConfigParser()
config.read("config.ini")

token = get_token(config)

MAILBOX = config["graph"]["mailbox"]

response = requests.get(
    f"https://graph.microsoft.com/v1.0/users/{MAILBOX}/messages"
    "?$top=5"
    "&$select=id,subject,receivedDateTime",
    headers={
        "Authorization": f"Bearer {token}"
    }
)

print("Status:", response.status_code)

data = response.json()

for msg in data.get("value", []):
    print(msg["receivedDateTime"])
    print(msg["subject"])
    print("-" * 50)