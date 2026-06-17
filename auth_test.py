# auth_test.py

import configparser
from modules.auth import get_token

config = configparser.ConfigParser()
config.read("config.ini")

token = get_token(config)

print("TOKEN SUCCESS")
print(token[:50] + "...")