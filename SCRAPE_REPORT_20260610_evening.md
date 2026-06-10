# Scrape Report — JS Sources — 2026-06-10 (evening)

**Run type:** scheduled `veille-scrape-js-sources` (autonomous)
**Outcome:** 0 injected — frontier exhausted, no in-window in-scope items.
**origin/main:** 385 items, oldest 2026-05-11, cutoff = **2026-05-11** (today − 30d).

## Method note (the durable lesson)
Applied the 30-day window gate to every candidate **before** dedup/inject. This is the
correction to the 06-09 and 06-10-morning mistakes where out-of-window items (absent from
origin/main *because already pruned*) were injected and then reverted. A candidate's absence
from origin/main is NOT evidence of novelty when the item is older than the cutoff.

This is the **third 0-item run today** (07:15 reverted to 0, 12:30 midday 0, this run 0) —
the JS frontier is reliably exhausted by the morning run.

## Per-source results

| Source | Frontier found | In DB? | Action |
|---|---|---|---|
| ACPR – Communiqués | SocGen 5/18 (in window) | yes | skip (dup) |
| ACPR – Communiqués | BdF/ACPR fraud-usurpation warning **27 Apr** | — | skip (out of window, day 44) |
| ACPR – Publications | — | — | none new |
| DOJ – Criminal Division | Huang 6/3 (MNF trade-based ML) | yes | skip (dup) |
| DOJ topical search | LA Fashion District ML+customs — `published 2025-09-30` | — | skip (out of window, day 253) |
| DOJ topical search | NJ $9M PPP fraud+ML | — | skip (domestic PPP, USAO not MNF, below scope) |
| DOJ topical search | Queens $653M (2022), 1MDB (5/27 in DB), TD Bank (old), Fraud-Div $1B omnibus, AirBit remission | mixed | skip (known false-pos / in DB / scope) |
| OFAC – Recent Actions | WebFetch dead (18+ runs); RSS owns to 6/5 | yes | skip |
| US Treasury – Sanctions Press | no new sb above 6/02 Nobitex (sb0519); sb0509/sb0507 already in DB | yes | skip |
| UN Security Council | 5/29 South Sudan (JS-blank, Chrome unavailable) | yes | skip |
| Conseil de l'UE | 5/28 Hamas/PIJ (JS-blank, Chrome unavailable) | yes | skip |
| Egmont Group | 6/4 pair + 6/1 Hennie | yes | skip |
| Wolfsberg Group | 5/22 Forum | yes | skip |
| GAFI/FATF | newest output ~3/3 (out of window) | — | skip |
| Interpol | nothing fresh in-scope/in-window | — | skip |
| CJUE | RSS-owned | — | skip |

## Flags for Maria (reiterated)
- **Drop the OFAC URL from this scrape's source list** — OFAC WebFetch has returned the stale
  5/8 snapshot for 18+ consecutive runs; the RSS path owns OFAC and is current to 6/5. The fetch
  slot is pure waste.
- **Hard-code the `published >= today−30d` gate into `scraper.py`** rather than relying on
  per-run discipline. The morning churn (16 out-of-window items injected then reverted) would
  have been prevented by an in-code gate. The stale OFAC/Treasury/DOJ WebFetch snapshot is a
  permanent out-of-window trap — its newest items are always ~30d old.
- **Cadence:** consider dropping the evening JS-scrape (or moving to once-daily). Three 0-item
  runs today; the frontier moves at most once a day.
