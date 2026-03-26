"""
Module presse — Scraping des flux RSS presse et filtrage par mots-clés LCB-FT.

Utilise les flux RSS publics des journaux (pas de scraping HTML).
Filtre les articles par mots-clés conformité/réglementation.
"""

import re
from datetime import datetime, timezone
from typing import Optional

import feedparser
from dateutil import parser as dateparser


# Keywords for filtering press articles (must contain at least one)
PRESS_KEYWORDS = [
    # Français
    "lcb-ft", "blanchiment", "conformité", "sanctions", "fraude",
    "régulateur", "acpr", "amf", "tracfin", "autorité bancaire",
    "établissement de crédit", "services de paiement",
    "crypto", "actif numérique", "psan",
    "financement du terrorisme", "gel des avoirs",
    "vigilance", "kyc", "due diligence",
    "amende", "pénalité", "mise en demeure",
    "directive", "règlement européen", "mica", "dora",
    "anti-blanchiment", "lutte contre le blanchiment",
    # English
    "aml", "compliance", "money laundering", "sanctions",
    "regulatory", "enforcement", "fintech", "regtech",
]


def _is_relevant(title: str, summary: str) -> bool:
    """Check if article matches regulatory keywords."""
    text = f"{title} {summary}".lower()
    return any(kw in text for kw in PRESS_KEYWORDS)


def fetch_press_feed(url: str, source_name: str) -> list[dict]:
    """
    Fetch a press RSS feed and filter for regulatory articles.

    Returns only articles that match at least one keyword.
    """
    try:
        feed = feedparser.parse(url)
    except Exception:
        return []

    items = []
    for entry in feed.entries:
        title = getattr(entry, "title", "Sans titre")
        summary_raw = getattr(entry, "summary", "") or getattr(entry, "description", "") or ""
        summary = re.sub(r"<[^>]+>", "", summary_raw).strip()

        if not _is_relevant(title, summary):
            continue

        # Parse date
        published = None
        for date_field in ("published", "updated", "created"):
            raw = getattr(entry, date_field, None)
            if raw:
                try:
                    published = dateparser.parse(raw)
                    break
                except Exception:
                    pass
        if not published:
            published = datetime.now(timezone.utc)

        items.append({
            "title": title,
            "url": getattr(entry, "link", ""),
            "author": getattr(entry, "author", ""),
            "published_at": published,
            "summary": summary[:500],
            "raw_text": summary[:3000],
        })

    return items
