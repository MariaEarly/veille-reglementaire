# Gmail Monitor Implementation Summary

## Overview

`gmail_monitor.py` is a Python script that monitors Gmail for regulatory emails and merges them into the `data.json` file used by the regulatory newsletter aggregator.

## File Location

```
/sessions/hopeful-eager-lamport/mnt/agregateur/gmail_monitor.py
```

## Key Features

### 1. Gmail Connection via IMAP
- Uses standard `imaplib` (Python stdlib)
- Connects to `imap.gmail.com:993` with SSL
- Authentication via Google App Password (not OAuth)
- No pip dependencies required

### 2. Email Sources Monitored
```python
REGULATORY_SENDERS = [
    {"email": "noreply@esma.europa.eu", "name": "ESMA (Email)", "category": "autorite_eu"},
    {"email": "no-reply@eba.europa.eu", "name": "EBA (Email)", "category": "autorite_eu"},
    {"email": "webmestre@acpr.banque-france.fr", "name": "ACPR (Email)", "category": "autorite_fr"},
]
```

### 3. Email Parsing
Extracts from each email:
- **Subject**: Email title
- **From**: Sender email
- **Date**: Publication timestamp (ISO format)
- **Body**: Plain text or HTML stripped of tags
- **Links**: All `href` attributes from HTML (for first URL as main link)

### 4. Item Generation
Creates items with the exact same schema as RSS ingestion:
```python
{
    "hash": "unique_sha1_hash[:16]",
    "source_name": "ESMA (Email)",
    "source_type": "email",
    "category": "autorite_eu",
    "title": "email_subject",
    "url": "first_link_from_body",
    "author": "noreply@esma.europa.eu",
    "published": "2026-03-25T10:30:00+00:00",
    "summary": "first_500_chars_of_body",
    "score": 45,  # Calculated using ingest.py scoring
    "doc_type": "COMMUNIQUÉ",  # Detected from title
    "action_class": "info",  # Classified from doc_type
    "status": "new",
    "early_brief": false,
    "ai_summary": null
}
```

### 5. Scoring & Classification Reuse
Imports functions from `ingest.py`:
- `score_item()` - Calculates compliance relevance score
- `detect_doc_type()` - Identifies document type (DÉCRET, ARRÊTÉ, etc.)
- `classify_action()` - Determines if item requires action or is informational
- `item_hash()` - Generates unique hash from subject + URL

### 6. Data Merging
- Loads existing `data.json`
- Deduplicates by hash (existing + new)
- Adds only new items
- Sorts by score (descending)
- Saves back to `data.json`

## Environment Variables

Required for execution:
- `GMAIL_USER`: Gmail address (e.g., `monitoring@example.com`)
- `GMAIL_APP_PASSWORD`: 16-character app password from Google

## Dependencies

**Python stdlib only** (no pip install needed):
- `json` - Data serialization
- `imaplib` - IMAP protocol
- `email` - Email parsing
- `hashlib` - Hash generation
- `re` - Regex for link extraction
- `datetime` - Timestamp handling
- `pathlib` - File operations

**External imports from ingest.py**:
- Scoring and classification functions
- Keyword lists for relevance detection

## Function Overview

| Function | Purpose |
|----------|---------|
| `decode_email_header()` | Handles MIME-encoded email headers |
| `strip_html()` | Removes HTML tags and decodes entities |
| `extract_links_from_html()` | Finds all `href` URLs in HTML |
| `get_email_body_text()` | Extracts plain text body |
| `get_email_body_html()` | Extracts HTML body |
| `connect_gmail()` | Opens IMAP connection |
| `search_emails_from_sender()` | Searches for emails from specific sender (last 24h) |
| `process_email()` | Parses email and creates item |
| `fetch_gmail_emails()` | Main email fetching loop |
| `load_data()` | Reads existing data.json |
| `save_data()` | Writes updated data.json |
| `merge_items()` | Deduplicates and adds new items |
| `main()` | Orchestrates the full pipeline |

## Execution Flow

```
1. Load existing data.json
   ↓
2. Connect to Gmail via IMAP
   ↓
3. For each regulatory sender:
   - Search for emails from last 24h
   - For each matching email:
     * Extract subject, body, links, date
     * Generate item with scoring
     * Classify document type and action
   ↓
4. Merge new items into data (dedup by hash)
   ↓
5. Sort by score (descending)
   ↓
6. Save to data.json
```

## GitHub Actions Integration

Example workflow (`.github/workflows/gmail-monitor.yml`):
```yaml
name: Gmail Monitor
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: cd agregateur && python3 gmail_monitor.py
        env:
          GMAIL_USER: ${{ secrets.GMAIL_USER }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
      - run: git add data.json && git commit -m "chore: Gmail monitor" || true
      - run: git push
```

## Error Handling

The script includes robust error handling:
- Graceful fallback if IMAP search fails
- Try/except on email parsing (charset issues)
- Handles missing headers or malformed emails
- Logs errors to stdout for GitHub Actions visibility
- Continues processing if individual emails fail

## Testing

Verify locally:
```bash
export GMAIL_USER="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-16-char-app-password"
cd /path/to/agregateur
python3 gmail_monitor.py
```

Output should show:
```
============================================================
Gmail Regulatory Monitor — 2026-03-25 10:30 UTC
============================================================
Loaded: 113 existing items
Fetching regulatory emails from Gmail...
  Connected to Gmail: your-email@gmail.com
  Searching emails from ESMA (Email)...
    Found N email(s) from noreply@esma.europa.eu
    Processed: [email subject]...
  ...
Added X new item(s) to data.json
Saved: 113+ total items
Done.
```

## Notes

- Script searches emails from **last 24 hours** on each run
- No OAuth complexity - uses standard Google App Passwords
- Deduplication prevents duplicates across runs
- Item scoring reuses same logic as RSS ingestion
- HTML links are parsed; first relevant link becomes main URL
- Body text is stripped to 500 characters for summary
