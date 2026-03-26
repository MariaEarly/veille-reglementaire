"""
Module Gmail IMAP — Scan des emails réglementaires.

Requiert un App Password Google (pas le mot de passe normal).
Configuration via variables d'environnement :
    GMAIL_USER=ton.email@gmail.com
    GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

Pour créer un App Password :
    1. https://myaccount.google.com/apppasswords
    2. Créer un mot de passe pour "Mail"
    3. Copier le mot de passe généré (16 caractères)
"""

import email
import email.utils
import imaplib
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Optional


# Keywords to filter relevant emails
FILTER_KEYWORDS = [
    "lcb-ft", "aml", "blanchiment", "sanctions", "conformité", "compliance",
    "tracfin", "acpr", "amf", "eba", "esma", "fatf", "gafi",
    "fraude", "fraud", "kyc", "vigilance", "mica", "dora",
    "réglementation", "regulation", "autorité", "authority",
    "pénalité", "amende", "fine", "penalty", "enforcement",
    "gel des avoirs", "embargo", "terrorist financing",
    "déclaration de soupçon", "suspicious transaction",
]


def _get_credentials() -> tuple[Optional[str], Optional[str]]:
    """Get Gmail credentials from environment."""
    user = os.environ.get("GMAIL_USER")
    password = os.environ.get("GMAIL_APP_PASSWORD")
    return user, password


def _is_relevant(subject: str, body: str) -> bool:
    """Check if email content matches regulatory keywords."""
    text = f"{subject} {body}".lower()
    return any(kw in text for kw in FILTER_KEYWORDS)


def _decode_header(header_value: str) -> str:
    """Decode email header (handles encoded-word syntax)."""
    if not header_value:
        return ""
    decoded_parts = email.header.decode_header(header_value)
    parts = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            parts.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(part)
    return " ".join(parts)


def _extract_text(msg: email.message.Message) -> str:
    """Extract plain text body from email message."""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
            elif content_type == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    html = payload.decode(charset, errors="replace")
                    # Strip HTML tags
                    return re.sub(r"<[^>]+>", " ", html).strip()
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="replace")
            if msg.get_content_type() == "text/html":
                return re.sub(r"<[^>]+>", " ", text).strip()
            return text
    return ""


def is_configured() -> bool:
    """Check if Gmail credentials are configured."""
    user, password = _get_credentials()
    return bool(user and password)


def fetch_gmail_items(days_back: int = 7, max_emails: int = 50) -> list[dict]:
    """
    Fetch regulatory emails from Gmail via IMAP.

    Returns list of items compatible with the Item model.
    Only returns emails that match regulatory keywords.
    """
    user, password = _get_credentials()
    if not user or not password:
        return []

    items = []

    try:
        # Connect to Gmail IMAP
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, password)
        mail.select("INBOX", readonly=True)

        # Search for recent emails
        since_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%d-%b-%Y")
        _, message_ids = mail.search(None, f"(SINCE {since_date})")

        if not message_ids[0]:
            mail.logout()
            return []

        ids = message_ids[0].split()
        # Process most recent first, cap at max_emails
        ids = ids[-max_emails:]

        for msg_id in reversed(ids):
            try:
                _, msg_data = mail.fetch(msg_id, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                subject = _decode_header(msg.get("Subject", ""))
                sender = _decode_header(msg.get("From", ""))
                body = _extract_text(msg)

                # Filter: only keep relevant emails
                if not _is_relevant(subject, body):
                    continue

                # Parse date
                date_str = msg.get("Date", "")
                published_at = None
                if date_str:
                    parsed = email.utils.parsedate_to_datetime(date_str)
                    if parsed:
                        published_at = parsed

                items.append({
                    "title": subject or "Email sans sujet",
                    "url": None,
                    "author": sender,
                    "published_at": published_at,
                    "summary": body[:500] if body else "",
                    "raw_text": body[:3000] if body else "",
                })

            except Exception:
                continue

        mail.logout()

    except imaplib.IMAP4.error as e:
        raise ConnectionError(f"Gmail IMAP error: {e}")
    except Exception as e:
        raise ConnectionError(f"Gmail connection failed: {e}")

    return items
