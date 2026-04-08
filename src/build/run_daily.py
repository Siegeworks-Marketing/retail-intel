from crawl.sources import SOURCES
from crawl.fetch import fetch
from crawl.parse import parse
from distill.events import build_events
from datetime import date
import json, os

today = date.today().isoformat()

os.makedirs("data/events", exist_ok=True)

all_events = []

for retailer, sources in SOURCES.items():
    for s in sources:
        html = fetch(s["url"])
        articles = parse(html, retailer)
        all_events.extend(build_events(articles))

with open(f"data/events/{today}.json", "w") as f:
    json.dump(all_events, f, indent=2)

print(f"Wrote {len(all_events)} events")
``