# Scrape Report — JS Sources — 2026-06-05 (evening)

**Run:** scheduled `veille-scrape-js-sources`, evening pass
**Outcome:** 1 item injected. origin/main 419 → 420.
**Commit:** `daeaadc..2349916` (data.json) + this report.

## Injected (1)

- **DOJ — Criminal Division** — "Member of an International Money Laundering Organization Pleads Guilty to Laundering Millions of Dollars in Drug Proceeds" (2026-06-03, score 30, `autorite_intl`, hash `b50486a30db4`).
  Puquan Huang (Chinese national, Buford GA) pleaded guilty to a conspiracy to launder several million dollars of fentanyl/cocaine proceeds via a **trade-based money laundering** scheme — bulk-cash pickups verified by US-currency serial codes, WeChat coordination with co-conspirators in China/Hong Kong/UAE, laundering through bulk-electronics exports. **Prosecuted by the MNF section** → clean in-scope per durable precedent (Zhen/Wu 5/22, Saab 5/18, Flores Silva 5/14). Was sitting behind the DOJ listing-page-1 frontier (still anchored 5/7); surfaced only via topical WebSearch, date confirmed via `meta-article:published_time = 2026-06-03T16:36:01`.

## Verified-and-skipped / no new items

- **Morning injections confirmed intact on origin/main** — Aspiration Partners (6/2), California Man Adi (5/18), Conseil Hamas/PIJ (5/28) all present. **Conseil clobbering pattern NOT observed for the 4th consecutive run — treat as resolved.** (Note: the *local working-copy* data.json was stale at 417 items / missing these three; origin/main is the source of truth at 419 pre-injection. Always build off `git show origin/main:data.json`, never the local file.)
- **OFAC** — 6/4 Cuba designations already in DB via RSS path. WebFetch staleness now **11+ consecutive runs** stuck at the 5/8 frontier — fully dead. *Reiterated flag: drop the OFAC URL from this scrape's source list; the RSS path owns it and this just wastes a fetch slot.*
- **Treasury Sanctions Press** — newest in DB is sb0519 (Nobitex, 6/2). No new in-scope `sb0NNN` since. Individual pages still WebFetch-blank.
- **Conseil de l'UE** — search surfaced only the 5/28 settlers item (already in DB). No new June press release.
- **UN Security Council** — frontier sc16374 South Sudan (5/29), already in DB. No newer in-scope item.
- **DOJ — Wells Fargo embezzlement (Haidar, 6/1)** — re-skipped (already skipped midday): single-branch local embezzlement, no cross-border/institutional-AML angle, USAO not MNF.
- **ACPR** (5/29 generic / Communiqués 5/18 SocGen), **Egmont** (5/26 Vice-Chair), **Wolfsberg** (5/22 Forum), **FATF** (5/6 Singapore, WebFetch still stale-2024 snippet), **Interpol** (5/18 cybercrime), **CJUE** (RSS-owned, skip) — all at frontiers already in DB.

## Notes for Maria

- **Cadence:** intraday second/third scrapes keep finding ≤1 item. The evening JS scrape remains low-value; the only catch this run (Huang) was a 6/3 backfill the morning/midday runs missed because it never hit DOJ listing page 1 — i.e. a topical-search gap, not a fresh-frontier gain. Consider keeping one daily JS scrape + the topical DOJ WebSearch rather than 2–3 passes.
- **OFAC URL drop** flagged again (11+ dead runs).
- **Local-clone staleness:** the working-copy data.json drifted to 417 and was missing 3 origin items. The temp-index push workflow is unaffected (it reads `origin/main`), but worth a cleanup of the local clone at some point.
