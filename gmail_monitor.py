#!/usr/bin/env python3
"""
Gmail Regulatory Newsletter Monitor.
Monitors Gmail for regulatory emails from ESMA, EBA, ACPR and outputs items
compatible with data.json format.

Uses IMAP + App Password for Gmail access (no OAuth complexity needed for CI/CD).
"""

import json
import os
import imaplib
import email
import hashlib
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.header import decode_header

# Import scoring functions from ingest.py
from ingest import (
    score_item,
    detect_doc_type,
    classify_action,
    matches_compliance_keywords,
    item_hash,
)

SCRIPT_DIR = Path(__file__).parent
DATA_FILE = SCRIPT_DIR / "data.json"

# Regulatory senders to monitor
REGULATORY_SENDERS = [
    {"email": "noreply@esma.europa.eu", "name": "ESMA (Email)", "category": "autorite_eu"},
    {"email": "no-reply@eba.europa.eu", "name": "EBA (Email)", "category": "autorite_eu"},
    {"email": "webmestre@acpr.banque-france.fr", "name": "ACPR (Email)", "category": "autorite_fr"},
]


def decode_email_header(header_value):
    """Safely decode email header (handles MIME encoded words)."""
    if not header_value:
        return ""
    try:
        decoded_parts = decode_header(header_value)
        result = []
        for part, charset in decoded_parts:
            if isinstance(part, bytes):
                try:
                    result.append(part.decode(charset or "utf-8", errors="ignore"))
                except Exception:
                    result.append(part.decode("utf-8", errors="ignore"))
            else:
                result.append(str(part))
        return "".join(result)
    except Exception:
        return str(header_value)


def strip_html(html_text):
    """Remove HTML tags and decode entities."""
    if not html_text:
        return ""
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", html_text)
    # Decode HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    # Clean up whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_links_from_html(html_text):
    """Extract all href URLs from HTML."""
    if not html_text:
        return []
    links = re.findall(r'href=["\']([^"\']+)["\']', html_text)
    # Filter out common junk/tracking links
    filtered = []
    for link in links:
        if not link.startswith("#") and link.startswith(("http", "https", "ftp")):
            filtered.append(link)
    return filtered


def get_email_body_text(msg):
    """Extract plain text body from email message."""
    body_text = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    charset = part.get_content_charset() or "utf-8"
                    payload = part.get_payload(decode=True)
                    body_text = payload.decode(charset, errors="ignore")
                    break
                except Exception:
                    pass
            elif content_type == "text/html" and not body_text:
                try:
                    charset = part.get_content_charset() or "utf-8"
                    payload = part.get_payload(decode=True)
                    html = payload.decode(charset, errors="ignore")
                    body_text = strip_html(html)
                    break
                except Exception:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or "utf-8"
            body_text = payload.decode(charset, errors="ignore")
        except Exception:
            body_text = msg.get_payload()
    return body_text


def get_email_body_html(msg):
    """Extract HTML body from email message (for link extraction)."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                try:
                    charset = part.get_content_charset() or "utf-8"
                    payload = part.get_payload(decode=True)
                    return payload.decode(charset, errors="ignore")
                except Exception:
                    pass
    return ""


def connect_gmail(email_user, app_password):
    """Connect to Gmail via IMAP."""
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(email_user, app_password)
        print(f"  Connected to Gmail: {email_user}")
        return mail
    except imaplib.IMAP4.error as e:
        print(f"  IMAP login failed: {e}")
        return None
    except Exception as e:
        print(f"  Connection error: {e}")
        return None


def search_emails_from_sender(mail, sender_email, hours=24):
    """Search emails from a specific sender in the last N hours."""
    try:
        mail.select("INBOX")
        # Gmail IMAP search: emails from sender in the last 24 hours
        cutoff_date = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime(
            "%d-%b-%Y"
        )
        search_query = f'FROM "{sender_email}" SINCE {cutoff_date}'
        status, message_ids = mail.search(None, "X-GM-RAW", search_query)

        if status != "OK":
            # Fallback to simpler search if X-GM-RAW doesn't work
            status, message_ids = mail.search(None, f'FROM "{sender_email}"')

        if status != "OK":
            print(f"    Search failed for {sender_email}")
            return []

        msg_ids = message_ids[0].split()
        print(f"    Found {len(msg_ids)} email(s) from {sender_email}")
        return msg_ids
    except Exception as e:
        print(f"    Search error for {sender_email}: {e}")
        return []


def process_email(mail, msg_id, sender_info):
    """Fetch and process a single email message."""
    try:
        status, msg_data = mail.fetch(msg_id, "(RFC822)")
        if status != "OK":
            return None

        msg = email.message_from_bytes(msg_data[0][1])

        # Extract email metadata
        subject = decode_email_header(msg.get("Subject", ""))
        sender = decode_email_header(msg.get("From", ""))
        date_str = msg.get("Date", "")

        # Parse date
        try:
            from email.utils import parsedate_to_datetime
            published_dt = parsedate_to_datetime(date_str)
            published = published_dt.isoformat()
        except Exception:
            published = datetime.now(timezone.utc).isoformat()

        # Extract body and links
        body_text = get_email_body_text(msg)
        body_html = get_email_body_html(msg)

        links = extract_links_from_html(body_html) if body_html else []

        # Clean up body text
        body_summary = strip_html(body_text)[:500]

        # If no text extracted, try HTML
        if not body_summary and body_html:
            body_summary = strip_html(body_html)[:500]

        if not subject or not body_summary:
            return None

        # Get first relevant link
        url = links[0] if links else sender_info["name"]

        # Create item
        item = {
            "hash": item_hash(subject, url),
            "source_name": sender_info["name"],
            "source_type": "email",
            "category": sender_info["category"],
            "title": subject,
            "url": url,
            "author": sender,
            "published": published,
            "summary": body_summary,
            "score": score_item(subject, body_summary, sender_info["category"]),
            "doc_type": detect_doc_type(subject),
            "action_class": None,
            "status": "new",
            "early_brief": False,
            "ai_summary": None,
        }

        # Set action_class
        item["action_class"] = classify_action(item["doc_type"], subject, item["score"])

        return item
    except Exception as e:
        print(f"    Error processing email {msg_id}: {e}")
        return None


def fetch_gmail_emails():
    """Fetch and parse emails from regulatory senders."""
    email_user = os.getenv("GMAIL_USER")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not email_user or not app_password:
        print("Missing GMAIL_USER or GMAIL_APP_PASSWORD env vars")
        return []

    mail = connect_gmail(email_user, app_password)
    if not mail:
        return []

    all_items = []
    try:
        for sender_info in REGULATORY_SENDERS:
            print(f"  Searching emails from {sender_info['name']}...")
            msg_ids = search_emails_from_sender(mail, sender_info["email"], hours=24)

            for msg_id in msg_ids:
                item = process_email(mail, msg_id, sender_info)
                if item:
                    all_items.append(item)
                    print(
                        f"    Processed: {item['title'][:60]}..."
                        if len(item['title']) > 60 else f"    Processed: {item['title']}"
                    )
    finally:
        try:
            mail.close()
            mail.logout()
        except Exception:
            pass

    return all_items


def load_data():
    """Load existing data.json."""
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data.json: {e}")
            pass
    return {"sources": [], "items": [], "last_update": None}


def save_data(data):
    """Save updated data.json."""
    data["last_update"] = datetime.now(timezone.utc).isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def merge_items(data, new_items):
    """Merge new items, deduplicating by hash."""
    existing_hashes = {item["hash"] for item in data["items"]}
    added = 0

    for item in new_items:
        if item["hash"] not in existing_hashes:
            data["items"].append(item)
            existing_hashes.add(item["hash"])
            added += 1

    return added


def main():
    """Main entry point."""
    print("=" * 60)
    print(
        f"Gmail Regulatory Monitor — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"
    )
    print("=" * 60)

    # Load existing data
    data = load_data()
    print(f"Loaded: {len(data['items'])} existing items")

    # Fetch and process emails
    print("\nFetching regulatory emails from Gmail...")
    new_items = fetch_gmail_emails()
    print(f"Parsed {len(new_items)} email(s)")

    # Merge into data
    if new_items:
        added = merge_items(data, new_items)
        print(f"Added {added} new item(s) to data.json")
    else:
        print("No new items to add")

    # Sort by score
    data["items"].sort(key=lambda x: x.get("score", 0), reverse=True)

    # Save
    save_data(data)
    print(f"\nSaved: {len(data['items'])} total items")
    print(f"File size: {DATA_FILE.stat().st_size / 1024:.1f} KB")
    print("Done.")


if __name__ == "__main__":
    main()
