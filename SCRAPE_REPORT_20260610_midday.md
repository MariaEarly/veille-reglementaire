# Scrape Report — JS Regulatory Sources

**Run:** 2026-06-10 ~12:30 UTC (midday)
**Outcome:** 0 injected (expected cadence)
**origin/main:** 383 items, oldest 2026-05-11, newest tip `f8d9642`
**30-day cutoff applied:** 2026-05-11 (gate applied to every candidate BEFORE dedup/inject)

## Summary

No new in-window, in-scope items. The only fresh in-scope candidate surfaced — DOJ Huang (6/3, MNF trade-based ML) — is **already present** in origin/main (hash `b50486a30db4`, injected 6/05 evening and still on the tip). Correct outcome is 0 injected, consistent with the recent cadence.

Note: the morning run (`SCRAPE_REPORT_20260610.md`) made the out-of-window mistake again (injected 16 day-33–183 items, then reverted in-run to 382; cron has since advanced to 383). This run applied the 30-day gate up front and avoided it.

## Source-by-source

| Source | Frontier / newest in-window | Action |
|---|---|---|
| ACPR — Communiqués | SocGen sanction 5/18 (in-window) | Already in DB (dedup); next item 4/27 = out of window |
| ACPR — Publications | (duplicates generic ACPR source) | Skip per 6/03 precedent |
| DOJ — Criminal Division | Listing page-1 anchored 5/7 (out of window); topical search → Huang 6/3 already in DB | 0 new |
| OFAC — Recent Actions | WebFetch dead (5/8 frontier, ~17 consecutive runs) | Skip + flag; RSS owns it |
| US Treasury — Sanctions Press | sb pages blank; no new sb above 6/02 Nobitex | 0 new |
| UN Security Council | Chrome unavailable; 5/29 South Sudan in DB | 0 new |
| Conseil de l'UE | Chrome unavailable; 5/28 Hamas/PIJ in DB | 0 new |
| GAFI/FATF | newest output ~3/3 (out of window) | 0 new |
| Wolfsberg Group | 5/22 Forum in DB | 0 new |
| Egmont Group | 6/1 Hennie + 6/4 pair all present | 0 new |
| Interpol | newest in-scope out of window | 0 new |
| CJUE | RSS-owned (skip per precedent) | skip |

## DOJ topical-search candidates evaluated

- **Huang** (6/3, MNF, trade-based ML, fentanyl/cocaine → bulk-electronics export HK/UAE) — confirmed `published_time=2026-06-03T16:36:01`, in scope, **already in DB** (`b50486a30db4`).
- 1MDB $6M forfeiture (5/27) — already in DB.
- Fraud Division "$1B" omnibus — skip per precedent (political framing, out-of-scope sub-cases).
- AirBit Club compensation process — skip per precedent (victim-remission notice).
- Queens Man $653M ML — false positive, `published_time=2022-02-22`.
- TD Bank guilty plea $1.8B — old (2024-era resolution).
- Edison NJ man 51 months internet-scam ML — below-scope (domestic USAO), skip per 6/08 precedent.

## Flags for Maria

- **OFAC URL should be dropped from this scrape's WebFetch list** — dead ~17 consecutive runs at the 5/8 frontier; the RSS path owns OFAC and keeps it current to 6/05+.
- **Cadence:** JS-source frontier is exhausted by the morning run on most days; midday/evening re-runs reliably add nothing. The intraday second scrape remains a cost-saving candidate to drop.
- **Morning-run churn:** the recurring out-of-window inject→push→revert cycle (6/09, 6/09 evening, 6/10 morning) is wasted work. The fix is mechanical — apply `published >= today−30d` at the candidate stage before any dedup/build. Worth hard-coding this gate into the scraper rather than relying on per-run discipline.
