#!/usr/bin/env python3
"""
One-time email ingestion: inject email newsletter items into data.json.
Run manually or via Cowork scheduled task.
"""
import json, hashlib, re, sys, os
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from ingest import (
    score_item, apply_time_decay, detect_doc_type, classify_action,
    normalize_title, normalize_title_short, normalize_url,
    is_off_topic_for_compliance, matches_compliance_keywords,
    CORE_COMPLIANCE_SOURCES, DATA_FILE
)

def item_hash(title, url):
    return hashlib.sha1(f"{title}|{url}".encode()).hexdigest()[:16]

def clean_url(url):
    """Strip tracking params from URLs."""
    url = re.sub(r'[?&](utm_\w+|mc_\w+|_mcp\w*)=[^&]*', '', url)
    url = re.sub(r'\?$', '', url)
    return url

def parse_email_items(emails):
    """Parse a list of email metadata dicts into aggregator items."""
    items = []
    for em in emails:
        subject = em.get("subject", "")
        sender = em.get("from_name", "")
        sender_email = em.get("from_email", "")
        date_iso = em.get("date_iso", "")
        snippet = em.get("snippet", "")
        body = em.get("body", "")

        # Determine source_name
        source_name = "Email"
        if "occrp" in sender_email.lower():
            source_name = "OCCRP"
        elif "esma" in sender_email.lower():
            source_name = "ESMA - Email Notification"
        elif "eba" in sender_email.lower():
            source_name = "EBA - Email Alert"
        elif "consilium" in sender_email.lower():
            source_name = "Conseil de l'UE - Email"
        elif "icij" in sender_email.lower():
            source_name = "ICIJ"
        elif "makecryptomakesense" in sender_email.lower():
            source_name = "MCMS - Crypto Regulatory"

        # Extract URLs from body
        urls = re.findall(r'https?://[^\s\)>]+', body or "")
        # Filter out unsubscribe, manage, tracking links
        good_urls = [u for u in urls if not any(k in u.lower() for k in
            ["unsubscribe", "manage/preferences", "mailchimp", "list-manage",
             "newsletter.consilium.europa.eu/mk/", "kit-mail3.com"])]

        # For single-article emails (OCCRP, Council, ICIJ): one item
        if source_name in ("OCCRP", "ICIJ"):
            url = clean_url(good_urls[0]) if good_urls else ""
            # Filter out non-compliance OCCRP articles
            combined = f"{subject} {snippet}".lower()
            compliance_terms = ["sanction", "money laundering", "fraud", "corruption",
                "bribery", "asset freeze", "crypto", "financial crime", "bank",
                "laundering", "embargo", "gel des avoirs", "blanchiment", "oligarch",
                "seized", "freeze", "enforcement", "compliance", "aml"]
            if not any(t in combined for t in compliance_terms):
                continue
            items.append({
                "title": subject,
                "url": url,
                "summary": snippet[:500],
                "published": date_iso,
                "source_name": source_name,
                "author": sender_email,
            })

        elif source_name == "Conseil de l'UE - Email":
            # Council emails: extract main URL from body
            council_urls = [u for u in good_urls if "consilium.europa.eu" in u and "/press/" in u]
            url = clean_url(council_urls[0]) if council_urls else (clean_url(good_urls[0]) if good_urls else "")
            items.append({
                "title": subject,
                "url": url,
                "summary": snippet[:500],
                "published": date_iso,
                "source_name": source_name,
                "author": sender_email,
            })

        elif source_name == "ESMA - Email Notification":
            # ESMA emails contain links to documents — extract each
            esma_links = re.findall(r'((?:Library Document|News|ESMA page|Hearing|Consultation)\s+(.+?)\s*:\s*(https://www\.esma\.europa\.eu/[^\s]+))', body or "")
            if esma_links:
                for _, doc_title, doc_url in esma_links:
                    doc_title = doc_title.strip()
                    items.append({
                        "title": f"ESMA: {doc_title}",
                        "url": clean_url(doc_url),
                        "summary": f"ESMA notification: {doc_title}",
                        "published": date_iso,
                        "source_name": source_name,
                        "author": sender_email,
                    })
            else:
                # Fallback: use subject
                items.append({
                    "title": subject,
                    "url": clean_url(good_urls[0]) if good_urls else "",
                    "summary": snippet[:500],
                    "published": date_iso,
                    "source_name": source_name,
                    "author": sender_email,
                })

        elif source_name == "EBA - Email Alert":
            # EBA digests: extract individual headlines
            # Pattern: "Title Press Release Description" or "Title News Description"
            eba_sections = re.findall(r'(?:Press Release|News)\s+[​\s]*(The .+?)(?=\s*(?:Press Release|News|Edit your)|$)', body or "", re.DOTALL)
            if eba_sections:
                for section in eba_sections[:5]:  # Max 5 items per digest
                    # First sentence as title
                    title = section.strip().split('\n')[0][:200]
                    items.append({
                        "title": title,
                        "url": "",  # EBA doesn't include direct URLs in digest text
                        "summary": section.strip()[:500],
                        "published": date_iso,
                        "source_name": source_name,
                        "author": sender_email,
                    })
            else:
                items.append({
                    "title": subject,
                    "url": "",
                    "summary": snippet[:500],
                    "published": date_iso,
                    "source_name": source_name,
                    "author": sender_email,
                })

        elif source_name == "MCMS - Crypto Regulatory":
            # MCMS weekly digest: extract individual regulatory signals
            # Pattern: [JURISDICTION] Title\nSeverity\nDescription
            mcms_items = re.findall(r'\[([A-Z]{2,})\]\s+(.+?)(?:\n|\r\n)(?:CRITICAL|HIGH)', body or "")
            for jurisdiction, title in mcms_items[:8]:
                title = title.strip()
                items.append({
                    "title": f"[{jurisdiction}] {title}",
                    "url": "",
                    "summary": f"MCMS Week 13 crypto regulatory signal: [{jurisdiction}] {title}",
                    "published": date_iso,
                    "source_name": source_name,
                    "author": sender_email,
                })
            if not mcms_items:
                items.append({
                    "title": subject,
                    "url": "",
                    "summary": snippet[:500],
                    "published": date_iso,
                    "source_name": source_name,
                    "author": sender_email,
                })

        else:
            items.append({
                "title": subject,
                "url": clean_url(good_urls[0]) if good_urls else "",
                "summary": snippet[:500],
                "published": date_iso,
                "source_name": source_name,
                "author": sender_email,
            })

    return items


def inject_into_data(email_items):
    """Score, dedup, and inject email items into data.json."""
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    existing_hashes = {it["hash"] for it in data["items"]}
    existing_titles = {normalize_title(it.get("title", "")) for it in data["items"]}
    existing_titles_short = {normalize_title_short(it.get("title", "")) for it in data["items"]}
    existing_urls = {normalize_url(it.get("url", "")) for it in data["items"] if it.get("url")}

    added = 0
    skipped = 0

    for em_item in email_items:
        title = em_item["title"]
        url = em_item.get("url", "")

        h = item_hash(title, url)
        if h in existing_hashes:
            skipped += 1
            continue

        norm = normalize_title(title)
        if norm and norm in existing_titles:
            skipped += 1
            continue

        if url:
            norm_url = normalize_url(url)
            if norm_url and norm_url in existing_urls:
                skipped += 1
                continue

        norm_short = normalize_title_short(title)
        if norm_short and len(norm_short) > 20 and norm_short in existing_titles_short:
            skipped += 1
            continue

        # Score
        summary = em_item.get("summary", "")
        base_score, breakdown = score_item(title, summary, "email")
        final_score, decay_label = apply_time_decay(base_score, em_item.get("published", ""))
        doc_type = detect_doc_type(title)
        action_class = classify_action(doc_type, title, final_score)

        item = {
            "hash": h,
            "source_name": em_item["source_name"],
            "source_type": "email",
            "category": "email",
            "title": title,
            "url": url,
            "author": em_item.get("author", ""),
            "published": em_item.get("published", ""),
            "summary": summary[:500],
            "score": final_score,
            "score_breakdown": f"{breakdown} | {decay_label}",
            "doc_type": doc_type,
            "action_class": action_class,
            "status": "new",
            "early_brief": False,
            "ai_summary": None,
        }

        data["items"].append(item)
        existing_hashes.add(h)
        existing_titles.add(norm)
        existing_titles_short.add(norm_short)
        if url:
            existing_urls.add(normalize_url(url))
        added += 1
        print(f"  + [{final_score:3d}] {em_item['source_name'][:25]:25s} | {title[:60]}")

    if added:
        # Re-sort
        _geo_prio = {"autorite_fr": 3, "autorite_eu": 2, "jurisprudence": 2, "autorite_intl": 1, "presse": 0, "social": 0, "email": 0}
        data["items"].sort(key=lambda x: (x.get("score", 0), _geo_prio.get(x.get("category", ""), 0), x.get("published", "")), reverse=True)
        data["last_update"] = datetime.now(timezone.utc).isoformat()
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    return added, skipped


if __name__ == "__main__":
    # This is called with email data passed as JSON on stdin
    emails = json.load(sys.stdin)
    items = parse_email_items(emails)
    print(f"Parsed {len(items)} items from {len(emails)} emails")
    added, skipped = inject_into_data(items)
    print(f"\nResult: {added} added, {skipped} skipped (duplicates)")
