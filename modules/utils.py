# utils.py
import os
from datetime import datetime


def build_zip_password(config):

    prefix = config["zip"]["password-prefix"]

    return f"{prefix}{datetime.now().year}"


def build_output_filename(base_name):

    return (
        f"{base_name}_"
        f"{datetime.now():%Y%m%d}.xlsx"
    )


def safe_delete(file_path):

    try:

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception:
        pass