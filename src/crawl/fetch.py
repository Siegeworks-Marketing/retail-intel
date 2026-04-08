import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HEADERS = {"User-Agent": "RetailIntelBot/1.0"}

_session = None

def _get_session():
    global _session
    if _session is None:
        s = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=(500,502,503,504))
        s.mount('https://', HTTPAdapter(max_retries=retries))
        s.mount('http://', HTTPAdapter(max_retries=retries))
        _session = s
    return _session

def fetch(url: str) -> str:
    s = _get_session()
    try:
        r = s.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        text = r.text or ""
        low = text[:4000].lower()
        soft_indicators = (
            'page not found', '404', 'not found', 'error 404',
            'cannot be found', "can't find", 'requested url was not found',
            'no longer available'
        )
        if any(k in low for k in soft_indicators) and len(text) < 3000:
            logging.warning("Soft-404-like response for %s (len=%d) — treating as empty", url, len(text))
            return ""
        return text
    except Exception as e:
        logging.warning("Failed to fetch %s: %s", url, e)
        return ""
