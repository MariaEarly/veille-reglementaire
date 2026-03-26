#!/usr/bin/env python3
"""
Veille Réglementaire — HTML Scraper for non-RSS sources.
Uses regex-based extraction on static HTML pages.
Returns items in same format as fetch_rss() from ingest.py.
"""

import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
import re
import json
from pathlib import Path

# Import scoring and classification functions from ingest.py
import sys
sys.path.insert(0, str(Path(__file__).parent))
from ingest import (
    score_item,
    detect_doc_type,
    classify_action,
    item_hash,
    is_off_topic_for_compliance,
    matches_compliance_keywords,
    EXCLUDE_KEYWORDS,
    CORE_COMPLIANCE_SOURCES,
)

# Configuration
USER_AGENT = "EarlyBrief-Veille/1.0 (+https://early-brief.com)"
REQUEST_TIMEOUT = 15

# ─────────────────────────────────────────────────────────────────────────────
# SCRAPE SOURCES
# ─────────────────────────────────────────────────────────────────────────────
# Sources that work with static HTML scraping (GitHub Actions compatible)
SCRAPE_SOURCES = [
    {
        "name": "FinCEN",
        "url": "https://www.fincen.gov/news-room",
        "type": "scrape",
        "category": "autorite_intl",
        "scraper": "fincen",
        "base_url": "https://www.fincen.gov",
    },
]

# Sources that require JavaScript rendering (Cowork Chrome / Playwright only)
# These are scraped via the Cowork scheduled task, not GitHub Actions
CHROME_ONLY_SOURCES = [
    {
        "name": "ACPR - Communiqués",
        "url": "https://acpr.banque-france.fr/fr/communiques-de-presse",
        "type": "scrape",
        "category": "autorite_fr",
        "scraper": "acpr",
        "base_url": "https://acpr.banque-france.fr",
    },
    {
        "name": "ACPR - Publications",
        "url": "https://acpr.banque-france.fr/fr/publications-acpr",
        "type": "scrape",
        "category": "autorite_fr",
        "scraper": "acpr",
        "base_url": "https://acpr.banque-france.fr",
    },
    {
        "name": "DOJ - Criminal Division",
        "url": "https://www.justice.gov/criminal/press-releases",
        "type": "scrape",
        "category": "autorite_intl",
        "scraper": "doj",
        "base_url": "https://www.justice.gov",
    },
    {
        "name": "GAFI/FATF",
        "url": "https://www.fatf-gafi.org/en/publications.html",
        "type": "scrape",
        "category": "autorite_intl",
        "scraper": "fatf",
        "base_url": "https://www.fatf-gafi.org",
    },
    {
        "name": "Wolfsberg Group",
        "url": "https://wolfsberg-group.org",
        "type": "scrape",
        "category": "autorite_intl",
        "scraper": "wolfsberg",
        "base_url": "https://wolfsberg-group.org",
    },
    {
        "name": "Egmont Group",
        "url": "https://egmontgroup.org/news/",
        "type": "scrape",
        "category": "autorite_intl",
        "scraper": "egmont",
        "base_url": "https://egmontgroup.org",
    },
    {
        "name": "Interpol",
        "url": "https://www.interpol.int/en/News-and-Events/News",
        "type": "scrape",
        "category": "autorite_intl",
        "scraper": "interpol",
        "base_url": "https://www.interpol.int",
    },
    {
        "name": "Conseil de l'UE",
        "url": "https://www.consilium.europa.eu/en/press/press-releases/",
        "type": "scrape",
        "category": "autorite_eu",
        "scraper": "conseil_ue",
        "base_url": "https://www.consilium.europa.eu",
    },
    {
        "name": "CJUE",
        "url": "https://curia.europa.eu/jcms/jcms/Jo2_7052/en/",
        "type": "scrape",
        "category": "autorite_eu",
        "scraper": "cjue",
        "base_url": "https://curia.europa.eu",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _fetch_html(url):
    """Fetch HTML content from URL, return decoded string or None."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
        })
        resp = urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT)
        return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"    Scraper fetch error {url}: {e}")
        return None


def _clean_html(text):
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&#039;", "'").replace("&quot;", '"')
    text = re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _make_item(title, url, date_str, summary, source_name, category):
    """Create a standard item dict, applying filters."""
    title = _clean_html(title).strip()
    summary = _clean_html(summary).strip() if summary else ""

    if not title or len(title) < 5:
        return None

    # Apply exclusion filters
    combined = f"{title} {summary}".lower()
    if any(ex in combined for ex in EXCLUDE_KEYWORDS):
        return None
    if is_off_topic_for_compliance(title, summary, source_name):
        return None
    # Scraped sources always require compliance keyword match
    if not matches_compliance_keywords(title, summary):
        return None

    sc, sc_breakdown = score_item(title, summary, category)
    doc_type = detect_doc_type(title)
    action_class = classify_action(doc_type, title, sc)

    # Parse date
    published = None
    if date_str:
        date_str = date_str.strip()
        for fmt in [
            "%B %d, %Y", "%b %d, %Y",  # March 24, 2026
            "%m/%d/%Y",                  # 03/10/2026
            "%d %B %Y", "%d %b %Y",     # 24 March 2026
            "%Y-%m-%d",                  # 2026-03-24
            "%d/%m/%Y",                  # 24/03/2026
            "%d %B %Y",                  # French: 24 mars 2026
        ]:
            try:
                published = datetime.strptime(date_str, fmt).isoformat()
                break
            except ValueError:
                continue
        # Try French month names
        if not published:
            fr_months = {
                "janvier": "01", "février": "02", "mars": "03", "avril": "04",
                "mai": "05", "juin": "06", "juillet": "07", "août": "08",
                "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12",
            }
            for fr, num in fr_months.items():
                if fr in date_str.lower():
                    try:
                        d = re.sub(fr, num, date_str.lower(), flags=re.IGNORECASE)
                        d = re.sub(r"[^\d/\s-]", "", d).strip()
                        # Try "24 03 2026" format
                        parts = d.split()
                        if len(parts) == 3:
                            published = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}T00:00:00"
                    except Exception:
                        pass
                    break

    if not published:
        published = datetime.now(timezone.utc).isoformat()

    return {
        "hash": item_hash(title, url),
        "source_name": source_name,
        "source_type": "scrape",
        "category": category,
        "title": title,
        "url": url,
        "author": "",
        "published": published,
        "summary": summary[:500],
        "score": sc,
        "score_breakdown": sc_breakdown,
        "doc_type": doc_type,
        "action_class": action_class,
        "status": "new",
        "early_brief": False,
        "ai_summary": None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SCRAPERS
# ─────────────────────────────────────────────────────────────────────────────

def scrape_acpr(config):
    """Scrape ACPR communiqués or publications page."""
    html = _fetch_html(config["url"])
    if not html:
        return []

    base = config["base_url"]
    items = []

    # ACPR pages use <a> tags with href pointing to /fr/... paths
    # Pattern: link with title text, followed by date somewhere nearby
    # Look for links to communiqués/publications
    link_pattern = re.compile(
        r'<a[^>]*href="(/fr/(?:communiques-de-presse|publications-et-statistiques/publications)/[^"]+)"[^>]*>\s*([^<]+)</a>',
        re.IGNORECASE
    )

    # Also look for date patterns near links
    date_pattern = re.compile(r'(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4})', re.IGNORECASE)

    matches = link_pattern.findall(html)
    dates = date_pattern.findall(html)

    for i, (path, title) in enumerate(matches[:30]):
        url = base + path
        date_str = dates[i] if i < len(dates) else ""
        item = _make_item(title, url, date_str, "", config["name"], config["category"])
        if item:
            items.append(item)

    return items


def scrape_fincen(config):
    """Scrape FinCEN news room."""
    html = _fetch_html(config["url"])
    if not html:
        return []

    base = config["base_url"]
    items = []

    # FinCEN: links to /news/ paths with dates in MM/DD/YYYY format
    # Pattern: date followed by link
    pattern = re.compile(
        r'(\d{2}/\d{2}/\d{4})\s*.*?<a[^>]*href="(/(?:news|resources)/[^"]+)"[^>]*>\s*([^<]+)</a>',
        re.DOTALL | re.IGNORECASE
    )

    for date_str, path, title in pattern.findall(html)[:30]:
        url = base + path
        item = _make_item(title, url, date_str, "", config["name"], config["category"])
        if item:
            items.append(item)

    return items


def scrape_doj(config):
    """Scrape DOJ Criminal Division press releases."""
    html = _fetch_html(config["url"])
    if not html:
        return []

    base = config["base_url"]
    items = []

    # DOJ: articles with links to /opa/pr/ or /criminal/press-releases/
    # Look for links in article-like structures
    pattern = re.compile(
        r'<a[^>]*href="(/(?:opa/pr|criminal/press-releases)/[^"]+)"[^>]*>\s*([^<]{20,})</a>',
        re.IGNORECASE
    )

    # Date pattern: Month DD, YYYY
    date_pattern = re.compile(r'((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4})')

    link_matches = pattern.findall(html)
    date_matches = date_pattern.findall(html)

    for i, (path, title) in enumerate(link_matches[:30]):
        # Skip social sharing links
        if "facebook" in path.lower() or "twitter" in path.lower() or "linkedin" in path.lower():
            continue
        url = base + path
        date_str = date_matches[i] if i < len(date_matches) else ""
        item = _make_item(title, url, date_str, "", config["name"], config["category"])
        if item:
            items.append(item)

    return items


# ─────────────────────────────────────────────────────────────────────────────
# DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────
SCRAPERS = {
    "acpr": scrape_acpr,
    "fincen": scrape_fincen,
    "doj": scrape_doj,
}


def scrape_source(config):
    """Dispatch to the appropriate scraper."""
    scraper_name = config.get("scraper", "")
    scraper_fn = SCRAPERS.get(scraper_name)
    if not scraper_fn:
        print(f"    Unknown scraper: {scraper_name}")
        return []
    try:
        return scraper_fn(config)
    except Exception as e:
        print(f"    Scraper error {config['name']}: {e}")
        return []


def scrape_all():
    """Scrape all configured sources. Returns list of items."""
    all_items = []
    for src in SCRAPE_SOURCES:
        print(f"  Scraping: {src['name']}...")
        items = scrape_source(src)
        print(f"    -> {len(items)} items")
        all_items.extend(items)
    return all_items


# ─────────────────────────────────────────────────────────────────────────────
# MAIN (for testing)
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Testing scrapers...\n")
    for src in SCRAPE_SOURCES:
        print(f"=== {src['name']} ===")
        items = scrape_source(src)
        print(f"  Found {len(items)} items")
        for it in items[:5]:
            print(f"  - [{it['score']:3d}] {it['title'][:80]}")
            print(f"    {it['url'][:80]}")
        print()
