from distill.taxonomy import classify

def build_events(articles: list) -> list:
    events = []
    for a in articles:
        category = classify(a['title'])
        why_it_matters = generate_impact_summary(a, category)
        
        events.append({
            'retailer': a['retailer'],
            'category': category,
            'title': a['title'],
            'source_url': a['url'],
            'pub_date': a.get('pub_date', ''),
            'source_name': a.get('source_name', ''),
            'why_it_matters': why_it_matters,
            'tier': a.get('tier', '3')  # default to tier 3 if not specified
        })
    return events

def generate_impact_summary(article: dict, category: str) -> str:
    """Generate a brief, impactful summary of why a headline matters for retail business."""
    title = article.get('title', '').lower()
    retailer = article.get('retailer', '')
    source = article.get('source_name', '')
    
    # keyword-based impact templates
    impact_map = {
        'Pricing & Promotions': {
            'keywords': ['price','discount','sale','rollback','margin','cost'],
            'summary': 'Signals pricing strategy and margin pressure — direct competitive indicator'
        },
        'Supply Chain & Logistics': {
            'keywords': ['delivery','fulfillment','warehouse','shipping','inventory','automation'],
            'summary': 'Cost and speed capability — affects fulfillment competition and unit economics'
        },
        'Store Footprint': {
            'keywords': ['store','opening','closure','expansion','footprint'],
            'summary': 'Market exit/entry signal — impacts competitive density and customer access'
        },
        'Healthcare Services': {
            'keywords': ['pharmacy','clinic','health','telehealth','service','healthcare'],
            'summary': 'Vertical integration play — expands customer wallet share and loyalty'
        },
        'Corporate Strategy': {
            'keywords': ['investor','annual','partnership','acquisition','merger','strategy','ai','technology'],
            'summary': 'Leadership priorities and future direction — shapes long-term competitive posture'
        }
    }
    
    # check category-specific keywords for more specifics
    if category in impact_map:
        keywords = impact_map[category]['keywords']
        base = impact_map[category]['summary']
        
        # add specificity based on content
        if any(kw in title for kw in ['ai','technology','automation']):
            return f"{base} | Tech focus indicates operational transformation"
        elif any(kw in title for kw in ['pricing','margin','discount']):
            return f"{base} | Price action may signal competitive pressure"
        elif any(kw in title for kw in ['partner','acquire','merge']):
            return f"{base} | M&A activity could reshape competitive landscape"
        else:
            return base
    
    # fallback: tie to retailer and source tier
    tier = article.get('tier', '3')
    if 'investor' in source.lower() or 'earnings' in source.lower():
        return "Official financial communication — reflects management view of business health and priorities"
    elif 'job' in source.lower():
        return "Hiring patterns indicate resource allocation to growth/transformation areas"
    elif 'press' in source.lower() or 'newsroom' in source.lower():
        return "Direct official announcement — highest priority signal from leadership"
    
    return "Market activity to track — assess for competitive or strategic implications"
