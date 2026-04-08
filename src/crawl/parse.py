from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
import logging
import re

def parse(html: str, retailer: str, base_url: str = "", source_name: str = "") -> list:
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    items = []

    # try to extract publication date from meta tags
    pub_date = extract_date(soup)

    for a in soup.find_all('a'):
        title = a.get_text(strip=True)
        href = a.get('href')
        if not href or not title:
            continue
        href = href.strip()
        if href.startswith('#') or href.startswith('javascript:'):
            continue
        try:
            url = urljoin(base_url, href) if base_url else href
        except Exception:
            url = href

        # require reasonably informative title
        if len(title) < 20:
            continue

        items.append({
            'retailer': retailer,
            'title': title,
            'url': url,
            'pub_date': pub_date,
            'source_name': source_name
        })

    logging.debug("Parsed %d items for %s", len(items), retailer)
    return items

def extract_date(soup) -> str:
    """Extract publication date from common meta tags and HTML patterns."""
    # try common meta tags
    for attr in ['article:published_time', 'datePublished', 'publish_date', 'Date']:
        meta = soup.find('meta', property=attr) or soup.find('meta', attrs={'name': attr})
        if meta and meta.get('content'):
            date_str = meta.get('content')
            try:
                dt = datetime.fromisoformat(date_str.split('T')[0])
                return dt.strftime('%Y-%m-%d')
            except:
                pass
    
    # try parsing from time tag
    time_tag = soup.find('time')
    if time_tag and time_tag.get('datetime'):
        try:
            dt = datetime.fromisoformat(time_tag.get('datetime').split('T')[0])
            return dt.strftime('%Y-%m-%d')
        except:
            pass
    
    # try common text patterns: "Published: Feb 15, 2026", "Jan 8 2026", etc.
    text = soup.get_text()[:2000]
    for pattern in [
        r'(?:published|dated|updated)[\s:]+([A-Za-z]+\s+\d{1,2},?\s+20\d{2})',
        r'([A-Za-z]+\s+\d{1,2},\s+20\d{2})',
    ]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                dt = datetime.strptime(match.group(1), '%B %d, %Y')
                return dt.strftime('%Y-%m-%d')
            except:
                pass
    
    return ""  # return empty if no date found
