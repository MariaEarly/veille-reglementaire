# Scrape Report — JS Sources — 2026-06-05 (midday)

**Run type:** Scheduled `veille-scrape-js-sources` (midday). Autonomous, no user present.
**Outcome:** **0 new items injected.** All sources at frontiers already in `data.json` (421 items on `origin/main` at run start). Two surfaced leads both rejected after verification.
**DB state at run start:** `origin/main` HEAD `003cdcc` (gmail monitor update 2026-06-05 10:28 UTC), 421 items.

This was the day's second scrape (the 06:31 morning run injected 3: Conseil 5/28 Hamas/PIJ, DOJ Aspiration 6/2, DOJ Adi 5/18). The JS-source frontier did not advance between morning and midday — consistent with the standing cadence observation that the frontier rarely moves twice a day.

---

## Per-source frontier check

| Source | DB frontier | Live check | Verdict |
|---|---|---|---|
| ACPR – Communiqués | 18 May (SocGen sanction) | WebFetch OK; page-1 top = 18 May SocGen | No new |
| ACPR – Publications | 29 May (reporting AMLA) via generic ACPR | — | No new (dup of generic ACPR source) |
| DOJ – Criminal Division | 2 Jun (Aspiration) | Listing page-1 anchored **7 May** (Akhter/Seibel) — permanent lag; topical search ran | No new in scope |
| OFAC – Recent Actions | 4 Jun (Cuba) | RSS-owned; WebFetch dead (10+ runs) | Skip per precedent |
| US Treasury – Sanctions Press | 2 Jun (sb0519 Nobitex) | Searched; no sb0520+ sanctions action | No new (see Houthi note) |
| UN Security Council | 29 May (sc16374 South Sudan) | Searched; newest = 21 May (in DB) / 13 Apr (out of window) | No new |
| Conseil de l'UE | 28 May (Hamas/PIJ, settlers); 26 May (Russia HR) | Searched; nothing newer than 26 May | No new |
| Wolfsberg | 22 May (Forum) | Per precedent (blank WebFetch; recurring-title traps) | No new |
| Egmont | 26 May (Vice-Chair) | Per precedent (JS-shell) | No new |
| FATF/GAFI | stale 2024 snippet | Per precedent (WebFetch useless) | No new |
| Interpol | 18 May (cybercrime MENA) | Per precedent | No new |
| CJUE | 4 Jun (via RSS) | RSS-owned — skip per precedent | Skip |

---

## Leads surfaced and rejected

**1. Treasury "Increases Pressure on Houthi Smuggling and Illicit Revenue Generation Networks" — REJECTED (recurring-title trap).**
A topical WebSearch summary asserted a **June 4, 2026** date and described "21 individuals/entities + 1 vessel, Iran-backed Ansarallah." Verification: every canonical URL resolved to **sb0367**, and the globalsecurity cross-ref is `.../2026/01/mil-260116-treasury01.htm` = **January 16, 2026** — ~5 months out of the 30-day window. The "June 4" date was a hallucinated/conflated search-summary date. This is exactly the recurring-title + summary-date trap documented in memory; always verify the sb-number and the globalsecurity `YYMMDD` cross-ref before trusting a Treasury lead. **No genuine new Treasury item this run.**

**2. DOJ — "Former Bank Employee Sentenced … Embezzling More Than $800,000" (Tamim Haidar, Wells Fargo, USAO-NDCA, 1 Jun) — SKIPPED (below scope).**
Title keyword-matches (bank fraud + money laundering), but it's a single-branch assistant-manager embezzlement of $800K, purely domestic, prosecuted by a U.S. Attorney's Office (not Criminal Division / MNF), no cross-border or institutional-AML angle. Below the Early Brief LCB-FT/sanctions/major-fraud bar, consistent with the "domestic-only small ML case stays OUT" precedents (5/27 evening, 6/04 evening Medicare). Flagged here so Maria can widen if she wants routine USAO embezzlement cases in.

All other DOJ topical hits (Aspiration 6/2, Bank Insider 5/28, Zhen/Wu) are already in the DB.

---

## Standing flags (carried forward)

- **OFAC WebFetch is dead — 10+ consecutive runs stuck at 5/8 frontier** while the RSS path carries OFAC to 6/4. Recommend dropping the OFAC URL from this scrape's source list entirely; it only wastes a fetch slot.
- **DOJ listing page-1 lag is permanent** (anchored 7 May again). Topical WebSearch remains the only reliable DOJ surface path.
- **Intraday cadence:** third+ effectively-zero second-run of the week. The midday/evening JS scrape continues to add little once the morning run has harvested the frontier; dropping to once-daily (or every-other-day for the second slot) remains a reasonable cost saving.

## Git action

No `data.json` change → **no data commit**. Report file pushed via the temp-index / commit-tree / direct-SHA workflow per standing practice.
