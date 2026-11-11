
import json
import ssl
import urllib.request

from config import BASE_URL, API_KEY, API_SECRET, SSL_CERT_PATH


def get_tokens():
    """Fetches orderToken and priceToken from the DFN REST API."""

    data = json.dumps({
        "apiKey": API_KEY,
        "apiSecret": API_SECRET
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",
        data=data,
        method="POST"
    )

    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")

    # Trust the self-signed Nginx server certificate
    ssl_context = ssl.create_default_context(cafile=SSL_CERT_PATH)

    try:
        with urllib.request.urlopen(
            req,
            context=ssl_context,
            timeout=30
        ) as response:

            result = json.loads(response.read().decode())

            return (
                result.get("orderToken"),
                result.get("priceToken")
            )

    except Exception as e:
        print(f"Failed to fetch token: {e}")
        return None, None
