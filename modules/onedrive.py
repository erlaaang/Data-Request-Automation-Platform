import os

import requests


def _request_with_retries(method, url, **kwargs):
    last_error = None
    for attempt in range(3):
        try:
            response = method(url, **kwargs)
            if response.status_code in (200, 201, 202):
                return response
            if response.status_code in (500, 502, 503, 504):
                raise requests.exceptions.RequestException(f"Transient server error: {response.status_code}")
            return response
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.ChunkedEncodingError) as exc:
            last_error = exc
            if attempt == 2:
                raise

    if last_error is not None:
        raise last_error

    raise RuntimeError("Upload request failed without a captured error")


def upload_file(
        token,
        drivebox,
        local_file,
        onedrive_folder,
        filename):

    print(
        f"Uploading {filename}..."
    )

    file_size = os.path.getsize(local_file)
    path = (
        f"https://graph.microsoft.com/v1.0/users/{drivebox}"
        f"/drive/root:/BRINS/Data Management 2026/Support Data 2026/{onedrive_folder}/{filename}"
    )

    if file_size <= 4 * 1024 * 1024:
        with open(local_file, "rb") as f:
            response = _request_with_retries(
                requests.put,
                f"{path}:/content",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/octet-stream"
                },
                data=f,
                timeout=(30, 600)
            )

        response.raise_for_status()
        item = response.json()
        print("Upload Success")
        return item["id"]

    session_payload = {
        "item": {
            "@microsoft.graph.conflictBehavior": "replace"
        }
    }

    session_response = _request_with_retries(
        requests.post,
        f"{path}:/createUploadSession",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json=session_payload,
        timeout=(30, 600)
    )
    session_response.raise_for_status()
    upload_url = session_response.json()["uploadUrl"]

    chunk_size = 5 * 1024 * 1024
    offset = 0

    with open(local_file, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break

            start = offset
            end = offset + len(chunk) - 1
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Length": str(len(chunk)),
                "Content-Range": f"bytes {start}-{end}/{file_size}"
            }

            upload_response = _request_with_retries(
                requests.put,
                upload_url,
                headers=headers,
                data=chunk,
                timeout=(30, 600)
            )

            if upload_response.status_code in (200, 201):
                item = upload_response.json()
                print("Upload Success")
                return item["id"]

            if upload_response.status_code != 202:
                upload_response.raise_for_status()

            offset += len(chunk)

    raise RuntimeError("Upload session did not complete successfully")

def create_share_link(
        token,
        drivebox,
        item_id):

    print(
        "Creating Share Link..."
    )

    response = _request_with_retries(
        requests.post,
        f"https://graph.microsoft.com/v1.0/users/{drivebox}"
        f"/drive/items/{item_id}/createLink",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "type": "view",
            "scope": "organization"
        },
        timeout=(30, 600)
    )

    response.raise_for_status()

    data = response.json()

    link = data["link"]["webUrl"]

    print(
        "Share Link Created"
    )

    return link