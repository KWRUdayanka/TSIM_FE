# auth.py
import json
import urllib.request
from config import BASE_URL, API_KEY, API_SECRET

def get_tokens():
    """Fetches orderToken and priceToken from the DFN REST API."""
    data = json.dumps({"apiKey": API_KEY, "apiSecret": API_SECRET}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/auth/login", data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('X-Forwarded-For', '127.0.0.1')
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return result.get("orderToken"), result.get("priceToken")
    except Exception as e:
        print(f"Failed to fetch token: {e}")
        return None, None