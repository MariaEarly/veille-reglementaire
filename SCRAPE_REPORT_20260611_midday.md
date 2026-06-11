# Scrape Report — JS Sources — 2026-06-11 (midday)

**Run type:** scheduled `veille-scrape-js-sources` (autonomous)
**Outcome:** **0 injected** — frontier exhausted; no in-window, in-scope, non-duplicate items.
**Baseline:** `origin/main` = 388 items (tip `6e2ec0e`). Window gate cutoff = today − 30d = **2026-05-12**.

## Method note
Applied the 30-day window gate (`published >= 2026-05-12`) to every candidate **before**
dedup/inject — the standing correction to the early-June over-injection churn. Absence from
`origin/main` is NOT evidence of novelty for an item that predates the cutoff (it was pruned).
Dedup/novelty verified against the fresh `origin/main` snapshot (not local HEAD), keyed on
hash/URL/slug — never a name-substring grep (defendant names live in the `summary` field).

This was the day's second run (the 06:05 UTC run already returned 0 at 386 items; cron has since
advanced the DB to 388). I focused on the one reliably-lagged source — DOJ via topical WebSearch —
rather than re-fetching the JS sources the morning run verified <6h ago.

## Per-source results

| Source | DB frontier (in-window) | Status |
|---|---|---|
| DOJ – Criminal Division | Huang 6/3 (intl ML org, trade-based ML) | listing anchored 5/7; topical search surfaced only known/out-of-scope (below) → **skip** |
| ACPR – Communiqués | SocGen 5/18 | at frontier in DB → **skip** |
| OFAC – Recent Actions | RSS to 6/10 | WebFetch dead (~20 runs); RSS owns it → **skip** |
| US Treasury – Sanctions Press | sb0519 6/2 (Nobitex) | sb pages blank; no new sb above 6/2 → **skip** |
| UN Security Council | sc16374 5/29 (South Sudan) | JS-blank; DB current → **skip** |
| Conseil de l'UE | 5/28 (Hamas/PIJ) | JS-blank; no new June canonical financial-sanction release → **skip** |
| Egmont Group | 6/4 pair | JS-redirect; DB current → **skip** |
| Wolfsberg / FATF / Interpol / CJUE | Wolfsberg 5/22, Interpol 5/18, CJUE 6/11 (RSS) | RSS-owned / no in-window in-scope → **skip** |

## DOJ topical-search candidates rejected
- **1MDB "$6M Additional Funds" (1MDB / Jho Low / Tan condo)** — search summary asserted *June 9*;
  the article-page `meta-article:published_time` is **2026-05-27**. Already in the DB (DOJ 5/27).
  Classic hallucinated-date trap — confirmed by opening the page, not trusting the summary.
- **Queens Man $653M ML conspiracy** — `published_time = 2022-02-22` (4 yrs old). Recurring false-positive.
- **United Cartels meth trafficker (DC indictment, 6/10)** — headline = drug trafficking, USAO/HSTF
  (not MNF); ML is a secondary count. Out of scope per the "pure-trafficking-without-MNF stays out" precedent.
- **Fraud Division "$1B nationwide" omnibus** — default-skip omnibus rollup (political framing, out-of-scope sub-cases).
- **TD Bank $1.8B BSA/ML guilty plea** — old 2024 resolution surfacing as a related-content link.

## Operational flags for Maria
- **Git locks still unremovable.** `.git/index.lock` + `.git/HEAD.lock` (dated 20 May) are
  permission-denied on `rm`; normal `git add`/`commit` fail. Standing workaround used again
  (fresh `GIT_INDEX_FILE` on outputs mount → `read-tree origin/main` → `commit-tree` →
  direct-SHA `git push -v`). Recommend clearing the lock files host-side.
- **Drop the OFAC URL** from this scrape's source list (~20 dead WebFetch runs; RSS owns it).
- **Hard-code the `published >= today−30d` gate into `scraper.py`** instead of per-run discipline —
  the stale DOJ/Treasury/OFAC/Consilium WebFetch snapshots are permanent out-of-window traps.
- **Cadence:** second-of-day runs reliably add 0 (this is the norm now). The single daily morning
  run plus the RSS path covers the JS frontier; consider dropping the intraday JS scrape.
