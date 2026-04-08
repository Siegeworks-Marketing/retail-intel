from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

def parse(html: str, retailer: str, base_url: str = "") -> list:
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    items = []

    for a in soup.find_all('a'):
        title = a.get_text(strip=True)
        href = a.get('href')
        if not href or not title:
            continue
        href = href.strip()
        if href.startswith('#') or href.startswith('javascript:'):
            continue
        # resolve relative URLs when possible
        try:
            url = urljoin(base_url, href) if base_url else href
        except Exception:
            url = href

        # require a reasonably informative title
        if len(title) < 20:
            continue

        items.append({
            'retailer': retailer,
            'title': title,
            'url': url
        })

    logging.debug("Parsed %d items for %s", len(items), retailer)
    return items
