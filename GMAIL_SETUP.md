# Gmail Monitor Setup

The `gmail_monitor.py` script monitors Gmail for regulatory emails from ESMA, EBA, and ACPR, and merges matching items into `data.json`.

## Requirements

- Python 3.8+
- Standard library modules (imaplib, email, json, re, etc.)
- Runs via IMAP + Google App Password (no OAuth complexity)

## Environment Variables

Set these in your GitHub Actions secrets or local environment:

```
GMAIL_USER="your-email@gmail.com"
GMAIL_APP_PASSWORD="your-16-char-app-password"
```

## Google App Password Setup

1. Enable 2-Step Verification on your Google Account
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer" (or relevant device)
4. Google will generate a 16-character app password
5. Add it to GitHub Actions secrets as `GMAIL_APP_PASSWORD`

## GitHub Actions Workflow

Example workflow file (`.github/workflows/gmail-monitor.yml`):

```yaml
name: Gmail Regulatory Monitor

on:
  schedule:
    # Run every 6 hours
    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install feedparser
      
      - name: Monitor Gmail
        env:
          GMAIL_USER: ${{ secrets.GMAIL_USER }}
          GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
        run: cd agregateur && python3 gmail_monitor.py
      
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add data.json
          git commit -m "chore: update data.json from Gmail monitor" || true
          git push
```

## Output Format

The script creates items in the same format as RSS ingestion:

```json
{
  "hash": "unique_hash",
  "source_name": "ESMA (Email)",
  "source_type": "email",
  "category": "autorite_eu",
  "title": "Email Subject",
  "url": "https://...",
  "author": "sender@esma.europa.eu",
  "published": "2026-03-25T10:30:00+00:00",
  "summary": "First 500 chars of email body",
  "score": 45,
  "doc_type": "COMMUNIQUÉ",
  "action_class": "info",
  "status": "new",
  "early_brief": false,
  "ai_summary": null
}
```

## Monitored Senders

- `noreply@esma.europa.eu` (ESMA - European Securities and Markets Authority)
- `no-reply@eba.europa.eu` (EBA - European Banking Authority)
- `webmestre@acpr.banque-france.fr` (ACPR - French prudential regulator)

The script searches for emails from the last 24 hours on each run.

## Debugging

Run locally with:

```bash
export GMAIL_USER="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
python3 gmail_monitor.py
```

Check the output for connection issues, parsing errors, or skipped items.
