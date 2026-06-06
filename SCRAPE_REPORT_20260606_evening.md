# Scrape Report — JS Sources — 2026-06-06 (evening)

**Run type:** scheduled `veille-scrape-js-sources` (evening)
**Outcome:** 0 new items injected. Report-only push.
**origin/main at run start:** `c558f4a`, 400 items (morning run had 414; intervening cron pruning to 400).

## Summary

Second run of the day. The 2026-06-06 morning run already found 0 new in-scope items; the JS-source frontier did not advance in the ~6 hours since. All sources confirmed at the same frontier already held in `origin/main`.

## Per-source results

| Source | Frontier in DB | Live check | New? |
|---|---|---|---|
| ACPR – Communiqués | 18 May (SocGen 20M€ sanction) | WebFetch OK; page-1 top item = 18 May SocGen | No |
| ACPR – Publications | (dup of generic ACPR source) | — | No |
| DOJ – Criminal Division | 03 Jun (Huang) | WebFetch OK; listing page-1 still anchored 7 May (permanent lag). Topical WebSearch surfaced only items already in DB (Huang 6/3 = `member-international-money-laundering-organization…`, Bank Insider, Georgian Citizen) or default-skips (Haidar 6/1 Wells-Fargo embezzlement = below-scope; Fraud Division "$1B" omnibus = skip; AirBit remission = skip) | No |
| OFAC – Recent Actions | 05 Jun | WebFetch dead (13+ runs); RSS owns it. `/recent-actions/20260605` (Iran + CT designations) already in DB | No |
| US Treasury – Sanctions Press | 02 Jun (sb0519 Nobitex) | sb pages blank to WebFetch; no canonical sb release above 6/02 surfaced. Search-summary "Economic Fury LPG Smuggling 6/5" had no verifiable distinct sb URL — companion to OFAC 6/05 already in DB | No |
| UN Security Council – Sanctions | 29 May (sc16374 S. Sudan) | WebSearch: nothing indexed newer than 5/29; sc16336 (Taliban, 4/13) out of window | No |
| Conseil de l'UE | 28 May (Hamas/PIJ + settlers) | WebSearch: no new June canonical `/press/press-releases/2026/06/…` financial-sanction release; Crimea extension to 23 Jun is a renewal of an existing measure, no new designation | No |
| CJUE | RSS-owned (skip) | — | No |
| Wolfsberg Group | 22 May (Forum) | Homepage blank to WebFetch (JS shell); no fresh article | No |
| Egmont Group | 26 May | Homepage JS-shell; WebSearch surfaced only 2024-2025 FATF/Egmont joint reports + Sept-2025 handbook (all out of window) | No |
| GAFI/FATF | (stale) | `publications.html` returns stale snippet; nothing new in window | No |
| Interpol | 18 May | No fresh in-scope financial-crime operation/report | No |

## Editorial notes / flags for Maria

- **Cadence:** this is the **5th effectively-zero second-run in ~10 days** (5/25 midday, 5/27 evening, 6/04 evening2, 6/05 midday, 6/06 evening). The JS-source frontier is consistently exhausted by the morning run. Recommend dropping the evening JS-scrape to every-other-day or morning-only — it reliably adds nothing.
- **OFAC WebFetch** dead 13+ consecutive runs (stale 5/8 snapshot vs RSS at 6/05). Recommend removing the OFAC URL from this scrape's WebFetch list entirely — the RSS path owns OFAC and this fetch slot is wasted every run.
- **DOJ listing page-1** permanently anchored at 7 May; topical WebSearch remains the only reliable surface path (used again this run, no new in-scope hits).

## Git
Report-only push (no data.json change).
