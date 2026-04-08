import requests

HEADERS = {"User-Agent": "RetailIntelBot/1.0"}

def fetch(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text
