"""
Module social — Ingestion des flux RSS.app (X/Twitter, LinkedIn).

Consomme les flux RSS générés par RSS.app pour les comptes sociaux
des institutions réglementaires. Filtre le bruit (events, HR, reposts)
et plafonne le score à 25 — ces items sont des signaux de détection,
pas des sources validées.
"""

import re
from datetime import datetime, timezone
from typing import Optional

import feedparser
from dateutil import parser as dateparser
from .scoring import is_social_noise, SOCIAL_NOISE_PATTERNS


def fetch_social_feed(url: str, source_name: str) -> list[dict]:
    """
    Fetch a social RSS feed (via RSS.app) and filter out noise.

    Returns only posts that pass the noise filter.
    Noise = events, recruitment, reposts, corporate comms.
    """
    try:
        feed = feedparser.parse(url)
    except Exception:
        return []

    items = []
    for entry in feed.entries:
        title = getattr(entry, "title", "Sans titre")
        summary_raw = (
            getattr(entry, "summary", "")
            or getattr(entry, "description", "")
            or ""
        )
        summary = re.sub(r"<[^>]+>", "", summary_raw).strip()

        # Filter out noise (events, HR, reposts, PR)
        if is_social_noise(title, summary):
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
            "author": source_name,  # attribute to the social account
            "published_at": published,
            "summary": summary[:500],
            "raw_text": summary[:3000],
        })

    return items
