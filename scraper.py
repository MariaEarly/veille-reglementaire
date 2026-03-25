#!/usr/bin/env python3
"""
Veille Réglementaire — HTML Scraper for non-RSS sources.
Implements scrapers for regulatory authorities without RSS feeds.
Returns items in same format as fetch_rss() from ingest.py.
"""

import urllib.request
import urllib.error
from html.parser import HTMLParser
from datetime import datetime, timezone
import re
import hashlib
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
)

# Configuration
USER_AGENT = "EarlyBrief-Veille/1.0 (+https://early-brief.com)"
REQUEST_TIMEOUT = 15

# ─────────────────────────────────────────────────────────────────────────────
# HTML PARSERS
# ─────────────────────────────────────────────────────────────────────────────

class ACPRParser(HTMLParser):
    """Parser for ACPR publications list (Autorité de contrôle prudentiel et de résolution)."""

    def __init__(self):
        super().__init__()
        self.items = []
        self.current_item = None
        self.in_publication = False
        self.in_title = False
        self.in_link = False
        self.in_date = False
        self.in_summary = False
        self.buffer = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Detect publication entries (typically in article or div with specific classes)
        if tag == "article" or (tag == "div" and "class" in attrs_dict and "publication" in attrs_dict["class"]):
            self.in_publication = True
            self.current_item = {"title": "", "url": "", "date": "", "summary": ""}

        # Links within publication entries
        if self.in_publication and tag == "a":
            href = attrs_dict.get("href", "")
            if href:
                # Make absolute URL if relative
                if href.startswith("/"):
                    href = "https://acpr.banque-france.fr" + href
                elif not href.startswith("http"):
                    href = "https://acpr.banque-france.fr/" + href
                self.current_item["url"] = href
                self.in_link = True

        # Check for date in common date patterns
        if self.in_publication and tag == "time":
            self.in_date = True
        elif self.in_publication and tag == "span" and "class" in attrs_dict and "date" in attrs_dict["class"].lower():
            self.in_date = True

    def handle_endtag(self, tag):
        if tag == "article" or (tag == "div" and self.in_publication):
            if self.current_item and self.current_item.get("title"):
                self.items.append(self.current_item)
            self.in_publication = False
            self.current_item = None
        elif tag == "a" and self.in_link:
            self.in_link = False
        elif tag == "time" and self.in_date:
            self.in_date = False

    def handle_data(self, data):
        if self.in_publication and self.current_item:
            text = data.strip()
            if self.in_link and not self.current_item["title"]:
                self.current_item["title"] = text
            elif self.in_date and not self.current_item["date"]:
                self.current_item["date"] = text


class FinCENParser(HTMLParser):
    """Parser for FinCEN news/announcements."""

    def __init__(self):
        super().__init__()
        self.items = []
        self.current_item = None
        self.in_article = False
        self.in_title = False
        self.in_date = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # FinCEN news items typically in article or div with news class
        if tag == "article" or (tag == "div" and "class" in attrs_dict and any(
            c in attrs_dict["class"].lower() for c in ["news", "item", "post"]
        )):
            self.in_article = True
            self.current_item = {"title": "", "url": "", "date": ""}

        # Link to the news item
        if self.in_article and tag == "a":
            href = attrs_dict.get("href", "")
            if href and not self.current_item["url"]:
                if href.startswith("/"):
                    href = "https://www.fincen.gov" + href
                elif not href.startswith("http"):
                    href = "https://www.fincen.gov/" + href
                self.current_item["url"] = href
                self.in_title = True

        # Date element
        if self.in_article and tag == "time":
            self.in_date = True
        elif self.in_article and tag == "span" and "class" in attrs_dict and "date" in attrs_dict["class"].lower():
            self.in_date = True

    def handle_endtag(self, tag):
        if tag == "article" and self.in_article:
            if self.current_item and self.current_item.get("title"):
                self.items.append(self.current_item)
            self.in_article = False
            self.current_item = None
        elif tag == "a" and self.in_title:
            self.in_title = False
        elif tag == "time" and self.in_date:
            self.in_date = False

    def handle_data(self, data):
        if self.in_article and self.current_item:
            text = data.strip()
            if self.in_title and not self.current_item["title"]:
                self.current_item["title"] = text
            elif self.in_date and not self.current_item["date"]:
                self.current_item["date"] = text


class DOJParser(HTMLParser):
    """Parser for US DOJ criminal fraud press releases."""

    def __init__(self):
        super().__init__()
        self.items = []
        self.current_item = None
        self.in_article = False
        self.in_title = False
        self.in_date = False
        self.buffer = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # DOJ press releases in article elements or divs with specific classes
        if tag == "article" or (tag == "div" and "class" in attrs_dict and any(
            c in attrs_dict["class"].lower() for c in ["release", "news", "press"]
        )):
            self.in_article = True
            self.current_item = {"title": "", "url": "", "date": ""}

        # Link to press release
        if self.in_article and tag == "a":
            href = attrs_dict.get("href", "")
            if href and not self.current_item["url"]:
                if href.startswith("/"):
                    href = "https://www.justice.gov" + href
                elif not href.startswith("http"):
                    href = "https://www.justice.gov/" + href
                self.current_item["url"] = href
                self.in_title = True

        # Date
        if self.in_article and tag == "time":
            self.in_date = True
        elif self.in_article and tag == "span" and "class" in attrs_dict and "date" in attrs_dict["class"].lower():
            self.in_date = True

    def handle_endtag(self, tag):
        if tag == "article" and self.in_article:
            if self.current_item and self.current_item.get("title"):
                self.items.append(self.current_item)
            self.in_article = False
            self.current_item = None
        elif tag == "a" and self.in_title:
            self.in_title = False
        elif tag == "time" and self.in_date:
            self.in_date = False

    def handle_data(self, data):
        if self.in_article and self.current_item:
            text = data.strip()
            if self.in_title and not self.current_item["title"]:
                self.current_item["title"] = text
            elif self.in_date and not self.current_item["date"]:
                self.current_item["date"] = text


class ConseilEUParser(HTMLParser):
    """Parser for European Council sanctions/press releases."""

    def __init__(self):
        super().__init__()
        self.items = []
        self.current_item = None
        self.in_article = False
        self.in_title = False
        self.in_date = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Press releases in article or div with specific classes
        if tag == "article" or (tag == "div" and "class" in attrs_dict and any(
            c in attrs_dict["class"].lower() for c in ["release", "item", "news", "press"]
        )):
            self.in_article = True
            self.current_item = {"title": "", "url": "", "date": ""}

        # Link
        if self.in_article and tag == "a":
            href = attrs_dict.get("href", "")
            if href and not self.current_item["url"]:
                if href.startswith("/"):
                    href = "https://www.consilium.europa.eu" + href
                elif not href.startswith("http"):
                    href = "https://www.consilium.europa.eu/" + href
                self.current_item["url"] = href
                self.in_title = True

        # Date
        if self.in_article and tag == "time":
            self.in_date = True
        elif self.in_article and tag == "span" and "class" in attrs_dict and "date" in attrs_dict["class"].lower():
            self.in_date = True

    def handle_endtag(self, tag):
        if tag == "article" and self.in_article:
            if self.current_item and self.current_item.get("title"):
                self.items.append(self.current_item)
            self.in_article = False
            self.current_item = None
        elif tag == "a" and self.in_title:
            self.in_title = False
        elif tag == "time" and self.in_date:
            self.in_date = False

    def handle_data(self, data):
        if self.in_article and self.current_item:
            text = data.strip()
            if self.in_title and not self.current_item["title"]:
                self.current_item["title"] = text
            elif self.in_date and not self.current_item["date"]:
                self.current_item["date"] = text


# ─────────────────────────────────────────────────────────────────────────────
# SCRAPING FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def fetch_html(url):
    """Fetch HTML content with proper headers and timeout."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT}
        )
        response = urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT)
        return response.read().decode("utf-8", errors="ignore")
    except urllib.error.URLError as e:
        print(f"    URLError fetching {url}: {e}")
        return None
    except urllib.error.HTTPError as e:
        print(f"    HTTP {e.code} fetching {url}")
        return None
    except Exception as e:
        print(f"    Error fetching {url}: {e}")
        return None


def parse_date(date_str):
    """Parse common date formats to ISO format."""
    if not date_str:
        return datetime.now(timezone.utc).isoformat()

    date_str = date_str.strip()

    # Try common formats
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d, %Y",
        "%b %d, %Y",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue

    # Fallback to current time
    return datetime.now(timezone.utc).isoformat()


def scrape_acpr():
    """Scrape ACPR (Autorité de contrôle prudentiel et de résolution) publications."""
    url = "https://acpr.banque-france.fr/publications"
    html = fetch_html(url)
    if not html:
        return []

    parser = ACPRParser()
    try:
        parser.feed(html)
    except Exception as e:
        print(f"    Parse error ACPR: {e}")
        return []

    items = []
    for entry in parser.items[:50]:
        title = entry.get("title", "").strip()
        link = entry.get("url", "").strip()
        date_str = entry.get("date", "")
        summary = entry.get("summary", "").strip()

        if not title or not link:
            continue

        # Filter out noise
        combined = f"{title} {summary}".lower()
        if any(ex in combined for ex in EXCLUDE_KEYWORDS):
            continue
        if is_off_topic_for_compliance(title, summary, "ACPR"):
            continue
        if not matches_compliance_keywords(title, summary):
            continue

        published = parse_date(date_str)
        score = score_item(title, summary, "autorite_fr")
        doc_type = detect_doc_type(title)
        action_class = classify_action(doc_type, title, score)

        items.append({
            "hash": item_hash(title, link),
            "source_name": "ACPR",
            "source_type": "scrape",
            "category": "autorite_fr",
            "title": title,
            "url": link,
            "author": "ACPR",
            "published": published,
            "summary": summary,
            "score": score,
            "doc_type": doc_type,
            "action_class": action_class,
            "status": "new",
            "early_brief": False,
            "ai_summary": None,
        })

    return items


def scrape_fincen():
    """Scrape FinCEN (Financial Crimes Enforcement Network) news."""
    url = "https://www.fincen.gov/news-room"
    html = fetch_html(url)
    if not html:
        return []

    parser = FinCENParser()
    try:
        parser.feed(html)
    except Exception as e:
        print(f"    Parse error FinCEN: {e}")
        return []

    items = []
    for entry in parser.items[:50]:
        title = entry.get("title", "").strip()
        link = entry.get("url", "").strip()
        date_str = entry.get("date", "")
        summary = ""

        if not title or not link:
            continue

        # Filter
        combined = f"{title} {summary}".lower()
        if any(ex in combined for ex in EXCLUDE_KEYWORDS):
            continue
        if is_off_topic_for_compliance(title, summary, "FinCEN"):
            continue
        if not matches_compliance_keywords(title, summary):
            continue

        published = parse_date(date_str)
        score = score_item(title, summary, "autorite_intl")
        doc_type = detect_doc_type(title)
        action_class = classify_action(doc_type, title, score)

        items.append({
            "hash": item_hash(title, link),
            "source_name": "FinCEN (US Financial Crimes Enforcement Network)",
            "source_type": "scrape",
            "category": "autorite_intl",
            "title": title,
            "url": link,
            "author": "FinCEN",
            "published": published,
            "summary": summary,
            "score": score,
            "doc_type": doc_type,
            "action_class": action_class,
            "status": "new",
            "early_brief": False,
            "ai_summary": None,
        })

    return items


def scrape_doj():
    """Scrape DOJ (Department of Justice) criminal fraud press releases."""
    url = "https://www.justice.gov/criminal/criminal-fraud"
    html = fetch_html(url)
    if not html:
        return []

    parser = DOJParser()
    try:
        parser.feed(html)
    except Exception as e:
        print(f"    Parse error DOJ: {e}")
        return []

    items = []
    for entry in parser.items[:50]:
        title = entry.get("title", "").strip()
        link = entry.get("url", "").strip()
        date_str = entry.get("date", "")
        summary = ""

        if not title or not link:
            continue

        # Filter
        combined = f"{title} {summary}".lower()
        if any(ex in combined for ex in EXCLUDE_KEYWORDS):
            continue
        if is_off_topic_for_compliance(title, summary, "DOJ"):
            continue
        if not matches_compliance_keywords(title, summary):
            continue

        published = parse_date(date_str)
        score = score_item(title, summary, "autorite_intl")
        doc_type = detect_doc_type(title)
        action_class = classify_action(doc_type, title, score)

        items.append({
            "hash": item_hash(title, link),
            "source_name": "DOJ (US Department of Justice - Financial Fraud)",
            "source_type": "scrape",
            "category": "autorite_intl",
            "title": title,
            "url": link,
            "author": "DOJ",
            "published": published,
            "summary": summary,
            "score": score,
            "doc_type": doc_type,
            "action_class": action_class,
            "status": "new",
            "early_brief": False,
            "ai_summary": None,
        })

    return items


def scrape_conseil_eu():
    """Scrape European Council press releases (with note about JS rendering)."""
    url = "https://www.consilium.europa.eu/en/press/press-releases/?filters=2030"
    html = fetch_html(url)
    if not html:
        print("    Note: Conseil de l'UE may use JS rendering. Headless browser recommended.")
        return []

    # Check if page contains actual content or is JS-rendered skeleton
    if "press-releases" not in html.lower() and "article" not in html.lower():
        print("    Note: Conseil de l'UE page appears JS-rendered. Implement headless browser if needed.")
        return []

    parser = ConseilEUParser()
    try:
        parser.feed(html)
    except Exception as e:
        print(f"    Parse error Conseil EU: {e}")
        return []

    items = []
    for entry in parser.items[:50]:
        title = entry.get("title", "").strip()
        link = entry.get("url", "").strip()
        date_str = entry.get("date", "")
        summary = ""

        if not title or not link:
            continue

        # Filter
        combined = f"{title} {summary}".lower()
        if any(ex in combined for ex in EXCLUDE_KEYWORDS):
            continue
        if is_off_topic_for_compliance(title, summary, "Conseil de l'UE"):
            continue
        if not matches_compliance_keywords(title, summary):
            continue

        published = parse_date(date_str)
        score = score_item(title, summary, "autorite_eu")
        doc_type = detect_doc_type(title)
        action_class = classify_action(doc_type, title, score)

        items.append({
            "hash": item_hash(title, link),
            "source_name": "Conseil de l'UE (Sanctions/Press Releases)",
            "source_type": "scrape",
            "category": "autorite_eu",
            "title": title,
            "url": link,
            "author": "Conseil de l'UE",
            "published": published,
            "summary": summary,
            "score": score,
            "doc_type": doc_type,
            "action_class": action_class,
            "status": "new",
            "early_brief": False,
            "ai_summary": None,
        })

    return items


# ─────────────────────────────────────────────────────────────────────────────
# SCRAPE SOURCE DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────

SCRAPE_SOURCES = [
    {
        "name": "ACPR",
        "url": "https://acpr.banque-france.fr/publications",
        "type": "scrape",
        "category": "autorite_fr",
        "scraper": "acpr",
    },
    {
        "name": "FinCEN (US Financial Crimes Enforcement Network)",
        "url": "https://www.fincen.gov/news-room",
        "type": "scrape",
        "category": "autorite_intl",
        "scraper": "fincen",
    },
    {
        "name": "DOJ (US Department of Justice - Financial Fraud)",
        "url": "https://www.justice.gov/criminal/criminal-fraud",
        "type": "scrape",
        "category": "autorite_intl",
        "scraper": "doj",
    },
    {
        "name": "Conseil de l'UE (Sanctions/Press Releases)",
        "url": "https://www.consilium.europa.eu/en/press/press-releases/?filters=2030",
        "type": "scrape",
        "category": "autorite_eu",
        "scraper": "conseil_eu",
    },
]


def scrape_source(source_config):
    """
    Main dispatcher for scraping a single source.

    Args:
        source_config: dict with keys: name, url, type, category, scraper

    Returns:
        list of items in fetch_rss() format
    """
    scraper_name = source_config.get("scraper", "").lower()

    if scraper_name == "acpr":
        return scrape_acpr()
    elif scraper_name == "fincen":
        return scrape_fincen()
    elif scraper_name == "doj":
        return scrape_doj()
    elif scraper_name == "conseil_eu":
        return scrape_conseil_eu()
    else:
        print(f"    Unknown scraper: {scraper_name}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
# MAIN / TEST
# ─────────────────────────────────────────────────────────────────────────────

def main():
    """Test/demo scraper."""
    print("=" * 70)
    print("Veille Réglementaire — HTML Scraper Test")
    print("=" * 70)

    for source_config in SCRAPE_SOURCES:
        print(f"\nScraping: {source_config['name']}...")
        items = scrape_source(source_config)
        print(f"  -> {len(items)} items parsed")
        if items:
            for item in items[:3]:
                print(f"     • {item['title'][:60]}... (score: {item['score']})")


if __name__ == "__main__":
    main()
