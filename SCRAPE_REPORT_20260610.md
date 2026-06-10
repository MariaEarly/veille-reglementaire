# Scrape Report — JS Sources — 2026-06-10

**Run:** scheduled `veille-scrape-js-sources` (autonomous)
**Outcome:** **0 items injected** (correct). origin/main stays at 382 items.

## 30-day window gate (the decisive filter)
The aggregator prunes anything older than today−30d. Today = 2026-06-10, so the cutoff is **2026-05-11** (the clean base's oldest item is exactly 2026-05-11, confirming the hard filter). Every compliance-relevant item surfaced by the JS sources this run is dated **before** that cutoff, so none are eligible. Items appear "absent from origin/main" precisely because they were already pruned — absence is not novelty for old items.

| Source | Freshest in-scope item found | Date | In window? |
|---|---|---|---|
| ACPR Communiqués | SocGen sanction (already in DB); fraude/usurpation | 5/18 / 4/27 | SocGen=dup; rest out |
| ACPR Publications | webinaire LCB-FT replay; bilan LCB-FT transmission | 3/2 / 2025-12-09 | out |
| DOJ Criminal Division | Oklahoma bank fraud | 5/7 (day 34) | out |
| US Treasury Sanctions Press | Iran UAV (sb0496); Iraqi oil (sb0492) | 5/8 / 5/7 | out |
| OFAC Recent Actions | May 7–8 designations (WebFetch stale frontier) | 5/7–5/8 | out |
| Wolfsberg Group | 2026 Forum (already in DB) | 5/22 | dup |
| CJUE | C-483/23 T Trust (freezing of assets) | ~5/8 | out + RSS-owned |
| GAFI/FATF | Stablecoins/unhosted wallets; cyber-enabled fraud | 3/3 / 2/24 | out |
| Interpol | UNODC fraud summit; financial fraud report | 3/17 / 3/16 | out |
| UN Security Council | — | — | WebFetch empty (no Chrome) |
| Egmont Group | — | — | JS-gated (no Chrome) |
| Conseil de l'UE | — | — | client-rendered/stale (no Chrome) |

## Source-health notes
- **No Chrome browser connected** this run, so Egmont, Consilium (Conseil de l'UE) and UN Security Council could not be refreshed (all JS-only). Their in-window state on origin/main is unchanged (Conseil 5/28, UN SC 5/29).
- **OFAC WebFetch still stale** — frontier stuck at 5/8 (18+ consecutive dead runs); RSS path owns OFAC. Recommend dropping the OFAC URL from this scrape's source list.
- FATF/Interpol returned content via WebFetch this run (no 403), but their newest outputs are all >30d old.

## Cadence
Another 0-eligible run, consistent with the standing pattern: the JS-source frontier is routinely older than the 30-day window. Worth Maria considering reducing this task's frequency.

## Process note (self-correction)
An earlier step injected the 16 out-of-window items and pushed them (commit 007609e, 398 items) before the 30-day gate was applied. This was caught and reverted in the same run — data.json restored to the clean 382-item base. The window check must run on candidates **before** dedup/inject.
