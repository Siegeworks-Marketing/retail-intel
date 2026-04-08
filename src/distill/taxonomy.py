def classify(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ['price', 'rollback', 'discount']):
        return 'Pricing & Promotions'
    if any(k in t for k in ['store', 'opening', 'closure']):
        return 'Store Footprint'
    if any(k in t for k in ['delivery', 'fulfillment', 'logistics']):
        return 'Supply Chain & Logistics'
    if any(k in t for k in ['pharmacy', 'clinic', 'health']):
        return 'Healthcare Services'
    return 'Corporate Strategy'
