import msal


def get_token(config):
    """
    Authenticate using Service Principal and return Graph token
    """

    tenant_id = config["graph"]["tenant-id"]
    client_id = config["graph"]["client-id"]
    client_secret = config["graph"]["client-secret"]

    app = msal.ConfidentialClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_secret
    )

    result = app.acquire_token_for_client(
        scopes=[
            "https://graph.microsoft.com/.default"
        ]
    )

    if "access_token" not in result:
        raise Exception(
            f"Graph Authentication Failed: {result}"
        )

    return result["access_token"]