from distill.taxonomy import classify

def build_events(articles: list) -> list:
    events = []
    for a in articles:
        events.append({
            'retailer': a['retailer'],
            'category': classify(a['title']),
            'title': a['title'],
            'source_url': a['url']
        })
    return events
