from datetime import datetime
from dateutil import parser as dateparser
import feedparser


def parse_rss_feed(url: str):
    feed = feedparser.parse(url)
    entries = []

    for entry in feed.entries:
        published = None
        if getattr(entry, "published", None):
            try:
                published = dateparser.parse(entry.published)
            except Exception:
                published = datetime.utcnow()

        entries.append({
            "title": getattr(entry, "title", "Untitled"),
            "url": getattr(entry, "link", None),
            "author": getattr(entry, "author", None),
            "published_at": published,
            "summary": getattr(entry, "summary", None),
            "raw_text": getattr(entry, "summary", None),
        })

    return entries
