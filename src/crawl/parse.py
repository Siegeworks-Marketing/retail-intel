from bs4 import BeautifulSoup

def parse(html: str, retailer: str) -> list:
    soup = BeautifulSoup(html, 'html.parser')
    items = []

    for a in soup.find_all('a'):
        title = a.get_text(strip=True)
        href = a.get('href')
        if title and href and len(title) > 40:
            items.append({
                'retailer': retailer,
                'title': title,
                'url': href
            })
    return items
