import argparse
import json
import logging
import os
from datetime import date
from difflib import SequenceMatcher

from crawl.sources import SOURCES, get_all_sources
from crawl.fetch import fetch
from crawl.parse import parse
from distill.events import build_events


def deduplicate_events(events: list, similarity_threshold: float = 0.75) -> list:
    """Remove duplicate/near-duplicate events based on URL and title similarity.
    
    Args:
        events: List of event dicts
        similarity_threshold: Fuzzy match threshold (0-1); 0.75+ = likely duplicate
    
    Returns:
        Deduplicated list, keeping highest-tier source for matches
    """
    if not events:
        return events
    
    # tier order for preference (lower tier = higher priority)
    tier_priority = {'1': 0, '2': 1, '3': 2}
    
    seen_urls = {}  # url -> event mapping
    deduped = []
    
    for event in events:
        url = event.get('source_url', '')
        title = event.get('title', '').lower()
        retailer = event.get('retailer', '')
        
        # exact URL match: skip if already seen, unless new one is higher tier
        if url and url in seen_urls:
            existing = seen_urls[url]
            new_tier_rank = tier_priority.get(event.get('tier', '3'), 99)
            existing_tier_rank = tier_priority.get(existing.get('tier', '3'), 99)
            if new_tier_rank < existing_tier_rank:
                # replace with higher tier version
                deduped.remove(existing)
                deduped.append(event)
                seen_urls[url] = event
            continue
        
        # fuzzy title match: check against recent titles from same retailer
        is_duplicate = False
        for existing in deduped[-20:]:  # check recent to avoid O(n²)
            if existing.get('retailer') != retailer:
                continue
            
            existing_title = existing.get('title', '').lower()
            # compute similarity ratio
            ratio = SequenceMatcher(None, title, existing_title).ratio()
            
            if ratio >= similarity_threshold:
                # likely duplicate; keep higher tier
                new_tier_rank = tier_priority.get(event.get('tier', '3'), 99)
                existing_tier_rank = tier_priority.get(existing.get('tier', '3'), 99)
                if new_tier_rank < existing_tier_rank:
                    deduped.remove(existing)
                    deduped.append(event)
                    if url:
                        seen_urls[url] = event
                is_duplicate = True
                break
        
        if not is_duplicate:
            deduped.append(event)
            if url:
                seen_urls[url] = event
    
    removed = len(events) - len(deduped)
    if removed > 0:
        logging.info("Deduplication removed %d duplicate(s)", removed)
    
    return deduped


def run(mode: str = "daily", tier: str = "1") -> list:
    """Crawl sources and build events.
    
    Args:
        mode: 'daily' or 'weekly'
        tier: '1', '2', or '3' (or 'all' for all tiers)
    """
    today = date.today().isoformat()
    out_dir = os.path.join("data", "events")
    os.makedirs(out_dir, exist_ok=True)

    all_events = []
    all_sources = get_all_sources()

    for retailer, sources in all_sources.items():
        # filter by tier if specified
        if tier != 'all':
            sources = [s for s in sources if s.get('tier') == tier]
        
        for s in sources:
            url = s.get("url")
            source_name = s.get("name", "")
            logging.info("Fetching %s (%s) - Tier %s", retailer, source_name, s.get('tier', 'N/A'))
            try:
                html = fetch(url)
                articles = parse(html, retailer, base_url=url, source_name=source_name)
                # inject tier into articles
                for a in articles:
                    a['tier'] = s.get('tier', '3')
                all_events.extend(build_events(articles))
            except Exception as e:
                logging.warning("Error processing %s (%s): %s", retailer, source_name, e)

    # deduplicate events
    all_events = deduplicate_events(all_events, similarity_threshold=0.75)

    out_path = os.path.join(out_dir, f"{today}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2)

    print(f"Wrote {len(all_events)} events to {out_path}")
    return all_events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("daily", "weekly"), default="daily")
    parser.add_argument("--tier", choices=("1", "2", "3", "all"), default="1",
                        help="Crawl tier 1 (daily), tier 2 (weekly), tier 3 (weekly), or all tiers")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    run(mode=args.mode, tier=args.tier)


if __name__ == "__main__":
    main()