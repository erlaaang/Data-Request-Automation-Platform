import requests


def upload_file(
        token,
        drivebox,
        local_file,
        onedrive_folder,
        filename):

    print(
        f"Uploading {filename}..."
    )

    with open(
            local_file,
            "rb"
    ) as f:

        response = requests.put(
            f"https://graph.microsoft.com/v1.0/users/{drivebox}"
            f"/drive/root:/BRINS/Data Management 2026/Support Data 2026/{onedrive_folder}/{filename}:/content",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/octet-stream"
            },
            data=f
        )

    response.raise_for_status()

    item = response.json()

    print("Upload Success")

    return item["id"]

def create_share_link(
        token,
        drivebox,
        item_id):

    print(
        "Creating Share Link..."
    )

    response = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{drivebox}"
        f"/drive/items/{item_id}/createLink",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "type": "view",
            "scope": "organization"
        }
    )

    response.raise_for_status()

    data = response.json()

    link = data["link"]["webUrl"]

    print(
        "Share Link Created"
    )

    return link