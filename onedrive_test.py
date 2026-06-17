import configparser

import requests

from modules.auth import get_token
from modules.onedrive import upload_file, create_share_link

config = configparser.ConfigParser()
config.read("config.ini")

token = get_token(config)

item_id = upload_file(
    token,
    config["graph"]["drivebox"],
    "temp/test.zip",
    "ReportAutomation",
    "test.zip"
)

print(item_id)

link = create_share_link(
    token,
    config["graph"]["drivebox"],
    item_id
)

print(link)
    