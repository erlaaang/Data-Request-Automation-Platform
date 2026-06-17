from modules.utils import *
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

print(build_zip_password(config))
print(build_output_filename("ClaimReport"))

from datetime import datetime


def build_zip_password(config):

    prefix = config["zip"]["password-prefix"]

    return (
        f"{prefix}"
        f"{datetime.now():%Y}"
    )