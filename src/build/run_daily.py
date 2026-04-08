import argparse
import json
import logging
import os
from datetime import date

from crawl.sources import SOURCES
from crawl.fetch import fetch
from crawl.parse import parse
from distill.events import build_events


def run(mode: str = "daily") -> list:
    today = date.today().isoformat()
    out_dir = os.path.join("data", "events")
    os.makedirs(out_dir, exist_ok=True)

    all_events = []

    for retailer, sources in SOURCES.items():
        for s in sources:
            url = s.get("url")
            logging.info("Fetching %s for %s", url, retailer)
            try:
                html = fetch(url)
                articles = parse(html, retailer, base_url=url)
                all_events.extend(build_events(articles))
            except Exception as e:
                logging.warning("Error processing %s (%s): %s", retailer, url, e)

    out_path = os.path.join(out_dir, f"{today}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_events, f, indent=2)

    print(f"Wrote {len(all_events)} events to {out_path}")
    return all_events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("daily", "weekly"), default="daily")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    run(mode=args.mode)


if __name__ == "__main__":
    main()