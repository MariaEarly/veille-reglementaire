# Scrape Report — JS Sources — 2026-06-06 (morning)

**Outcome: 0 new items injected.** All JS-source frontiers are already in `data.json` (origin/main = 414 items) or the freshest candidates fall outside the 30-day window (cutoff **2026-05-07**). Report-only push; no change to `data.json`.

## Per-source disposition

| Source | Method | Frontier in DB | Result |
|---|---|---|---|
| ACPR – Communiqués | WebFetch (OK) | 2026-05-18 (SocGen) | At frontier. Listing's "à la une" = 18 May SocGen sanction (already in DB); next items 27/21/16/13 Apr = out of window. **Nothing new.** |
| ACPR – Publications | (skipped) | — | Per precedent, listing items duplicate the generic `ACPR` source (frontier 6/04) via content, not URL → would create dups. **Skipped.** |
| DOJ – Criminal Division | WebFetch (OK) + topical WebSearch | 2026-06-03 (Huang) | Listing page-1 still anchored **5/7** (Akhter) — permanent lag. Topical search surfaced only known/out-of-scope items (see below). **Nothing new.** |
| OFAC – Recent Actions | WebFetch (DEAD) | 2026-06-05 (via RSS) | WebFetch stale **12+ consecutive runs** at 5/8 frontier. RSS path owns OFAC and is current to 6/05. **Confirm + flag; no inject.** |
| US Treasury – Sanctions Press | WebFetch (blank) + WebSearch | 2026-06-02 (sb0519 Nobitex) | Individual `sb0NNN` pages blank as usual. Search surfaced no new `sb` release above the 6/02 frontier; the "Economic Fury" hits (sb0496 etc.) are older/already covered. **Nothing new.** |
| UN Security Council – Sanctions | WebSearch (blank homepage) | 2026-05-29 (sc16374 South Sudan) | Newest indexed item = 5/21 ISIL/Al-Qaida removal (behind frontier); Consolidated List last updated 21 May. No June press release. **Nothing new.** |
| Wolfsberg Group | WebSearch (blank homepage) | 2026-05-22 (Forum) | Freshest substantive item = "Second Statement on Effective Monitoring for Suspicious Activity / AI in SAR", dated **2026-04-20** = out of window. **Nothing new.** |
| Egmont Group | WebSearch (JS shell) | 2026-05-26 | EC met 12–13 May; "International Day of the FIU" = 9 June (future, not yet an article). No June news item. **Nothing new.** |
| CJUE | (skipped) | RSS-owned | Covered by RSS feed `CJUE - Cour de Justice UE` (frontier 6/04). This scrape only exposes PDF URLs that bypass dedup → skip to avoid dups. **Skipped.** |
| Conseil de l'UE | WebSearch (JS pages) | 2026-05-28 (Hamas/PIJ + settlers) | Search returned only framework/explainer pages; no new canonical dated press release. Russia regime "extended until Sep 2026" surfaced but no fresh standalone June release URL. **Nothing new.** |
| GAFI/FATF | WebSearch (stale WebFetch) | — | Newest = 13 Feb 2026 grey/black list. Next list update due later in 2026. **Nothing new.** |
| Interpol | WebSearch (article pages unfetchable) | 2026-05-18 | "Operation Shadow Storm" looks fresh but launched at the **March 2026** Global Fraud Summit (out of window); 2026 Fraud Threat Assessment also March. **Nothing new.** |

## DOJ topical-search items reviewed (all rejected)

- **Huang** (6/3, trade-based ML, MNF) — already in DB (injected 6/05 evening).
- **Haidar** (Wells Fargo $800K embezzlement, 6/1, USAO-NDCA) — below scope per 6/05 midday precedent (routine single-institution embezzlement, no cross-border/institutional-AML angle). Skip.
- **Zhen/Wu** (transnational cartel-fund ML) — already in DB (5/22).
- **Bank Insider** (two-institution fraud facilitation) — already in DB (5/28).
- **Fraud Division "$1B second straight week" omnibus** — political-framing omnibus rollup; skip per 5/27-evening precedent.
- **AirBit Club compensation process** — victim-remission administrative notice, not a new enforcement action; skip per 6/03 precedent.

## Flags for Maria

1. **OFAC WebFetch is fully dead (12+ runs)** — reiterating the standing recommendation to drop the OFAC URL from this scrape's source list; the RSS path covers it and the fetch slot is wasted.
2. **Cadence:** this is another effectively-exhausted run — the JS-source frontier is consistently fully harvested by the prior day's runs. The morning JS scrape continues to find 0–1 genuinely new items; the intraday second scrape adds nothing. Worth considering reducing JS-scrape frequency.
3. No editorial overrides this run. The usual default-skip categories (migration/visa restrictive measures, generic Interpol policing, domestic-only Medicare/embezzlement ML, governance/budget Treasury releases, victim-remission notices) had no borderline cases worth your attention today.
