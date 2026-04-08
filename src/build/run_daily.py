import argparse
import json
import logging
import os
from datetime import date

from crawl.sources import SOURCES, get_all_sources
from crawl.fetch import fetch
from crawl.parse import parse
from distill.events import build_events


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