# JS-Source Scrape Report — 2026-06-11 (run 2 / later)

**Run:** scheduled `veille-scrape-js-sources` (autonomous)
**origin/main:** 384 → 386 items · data push `56c4c62..6757388`
**30-day cutoff applied up front:** 2026-05-12 (today − 30d)

## Reconciliation with the earlier 2026-06-11 run

The morning run (`SCRAPE_REPORT_20260611.md`) reported **0 injected**, but its WebFetch
returned a **stale 2017 archive for Conseil de l'UE** and a **JS redirect for Egmont** — so it
never saw the two items below. This run got **live renders** for both sources and found them
genuinely new and in-window. These are not out-of-window backfills (the recurring early-June
trap); both publish dates are ≥ cutoff. Hashes verified absent from fresh `origin/main` before push.

## Injected (2)

| Source | Date | Score | Item |
|---|---|---|---|
| Conseil de l'UE | 2026-06-08 | 37 | Freedom of navigation in the Strait of Hormuz: EU lists two individuals and one entity |
| Egmont Group | 2026-06-09 | 30 | International cooperation is central to effective financial intelligence |

**Conseil 6/8 — Strait of Hormuz.** CFSP asset-freeze + travel-ban designation (2 individuals + 1 entity) under the Iran freedom-of-navigation framework the Council extended on 22 May. Listed: the Hormozgan Provincial Command of the IRGC Navy (vessel screening + transit-toll system), Mohammad Akbarzadeh (IRGCN Deputy Commander, Political Affairs), and Hamid Hosseini (Iran Oil/Gas/Petrochemical Exporters' Union). Council Decision (CFSP) 2026/1226 + Implementing Reg. 2026/1225. Clean in-scope financial sanction; verified canonical dedup-safe URL (`/press/press-releases/2026/06/08/...`) and `SORT_DATE 20260608`.

**Egmont 6/9 — International cooperation.** International FIU Day post; Chair Franków-Jaśkiewicz on cross-border FIU cooperation and financial-intelligence quality. Borderline commemorative but injected per the consistent Egmont-institutional-inclusion precedent (FIU Day 6/4, annual report, governance items all in DB). Flagged for Maria to drop if she wants awareness posts out.

## Evaluated and SKIPPED

- **DOJ "L.A. Fashion District Wholesaler / C'est Toi Jeans" (trade-based ML + customs)** — topical-search hit, but `published_time = 2025-09-30` (8 months old). Out-of-window false positive.
- **DOJ topical search** otherwise surfaced only known/out-of-scope: Huang 6/3 (in DB), Queens $653M (2022 false-pos), 1MDB (in DB), TD Bank $1.8B (2024), Fraud-Division "$1B" omnibus (skip), Edison-NJ internet-scam ML (below-scope/domestic), Illinois Ponzi / NJ PPP (local USAO fraud, no AML/cross-border angle).
- **DOJ Orange County $100M bank fraud (6/10)** and **Citron Research stock manipulation (6/1)** — in-window but below the institutional-AML/sanctions bar; skipped per recent below-scope precedent. Flagged.
- **Treasury sb0509 (5/28), sb0510 (5/28)** — already in DB.
- **OFAC 6/9 "Cyber Army of Russia Reborn"** — search returned a Biden-era `jy2473` URL = pre-2025 trap (original 2024 CARR action). OFAC RSS-owned (DB frontier 6/10). Skipped.
- **Treasury 6/5 Houthi/Iran LPG smuggling** — OFAC-6/5 companion, no distinct `sb` URL; OFAC side already in DB via RSS. Skipped.
- **ACPR Communiqués** — frontier 5/18 SocGen (in DB); next page-1 item 4/27 = out-of-window. Nothing new.

## Source status notes

- The morning run's stale-render miss on Conseil/Egmont is the operational lesson here:
  **when a JS source returns an obviously stale body (2017 archive, redirect), do not treat it as
  "frontier exhausted" — retry the fetch later / via the individual article URL.** Both pages were
  cleanly fetchable this run.
- **OFAC WebFetch dead 18+ runs**; `jy####` Treasury URLs = pre-2025/out-of-window (trap).
- **DOJ listing page-1** anchored 5/7; topical WebSearch is the only reliable surface path (always read `meta-article:published_time`).
- **30-day gate held** — excluded the recurring stale-snapshot out-of-window items that caused the 6/09 + 6/10-morning churn.

## Push workflow

Temp-index on outputs mount (`GIT_INDEX_FILE=…/mnt/outputs/gitidx.$$`, `rm -f` no-mktemp), `read-tree origin/main` → index 3898 bytes, tree 37 entries → `commit-tree` → `git push -v <SHA>:refs/heads/main`. Landed first try `56c4c62..6757388`. `tmp_obj_* Operation not permitted` warnings cosmetic.
