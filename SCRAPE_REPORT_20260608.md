# Scrape Report — JS Sources — 2026-06-08 (17:11 UTC)

**Result: 0 new items injected.** All JS-rendered sources at the frontier already present in `origin/main` (368 items). Report-only push; no data.json commit.

## Source-by-source

| Source | Frontier in DB | This run | Decision |
|---|---|---|---|
| ACPR – Communiqués | 18 May (SocGen, blâme + 20 M€) | Listing newest = 18 May SocGen | At frontier — skip |
| ACPR – Publications | 22 May (N°50) / 21 May (Rapport annuel) | Listing newest = 22 May N°50, 21 May Rapport annuel | Both duplicate generic `ACPR` source — skip |
| DOJ – Criminal Division | 3 Jun (Huang, intl ML org) | Huang 6/3 in DB; no in-scope /opa/pr dated 6/4–6/8 | Skip (see leads below) |
| OFAC – Recent Actions | 5 Jun (via RSS) | WebFetch dead 15+ runs; RSS owns it | Skip + flag |
| US Treasury – Sanctions Press | 2 Jun (sb0519 Nobitex) | "6/5 Russia/Kyrgyz Keremet" = recurring-title false positive | Skip (see leads) |
| UN Security Council | 29 May (sc16374 South Sudan) | No new June press release indexed | At frontier — skip |
| Conseil de l'UE | 28 May (Hamas/PIJ + 10 indiv) | No new June canonical financial-sanction release | At frontier — skip |
| Egmont Group | 4 Jun (UNIDROIT art-market + FIU Day) | No new article beyond 6/4 pair | At frontier — skip |
| Wolfsberg Group | 22 May (Forum) | /news not in provenance this run; nothing newer expected | Skip |
| FATF / GAFI | (Feb grey list) | Feb 2026 grey list; no June publication | Stale — skip |
| Interpol | 18 May | Shadow Storm + Fraud Threat Assessment = March 2026 (out of window) | Skip per precedent |
| CJUE | RSS-owned (`CJUE - Cour de Justice UE`, 4 Jun) | — | RSS-owned, skip |

## Leads investigated and rejected

- **Treasury "6/5 Russia/China/Kyrgyz Keremet Bank sanctions evasion"** — the WebSearch summary asserted June 5 2026, but every canonical URL resolves to `jy2785` (Biden-era prefix) and globalsecurity cross-ref `russia-250115` = **15 January 2025**. Classic recurring-title hallucinated-date trap. Rejected.
- **DOJ "Queens Man $653M Money Laundering Conspiracy"** — surfaced again in topical search; `published_time = 2022-02-22` (4 yrs old) per 6/07-evening memory. Rejected.
- **DOJ Haidar (Wells Fargo $800K embezzlement, 6/1, USAO-NDCA)** — single-branch local embezzlement, no cross-border/institutional-AML angle, USAO not MNF. Below-scope per 6/05-midday precedent. Skip.
- **DOJ "Fraud Division $1B crackdown" omnibus + AirBit remission** — default-skip per precedent (political framing / victim-remission notice).
- **Interpol Operation Shadow Storm** — would be in-scope (scam-centre fraud + ML task force) but launched at the March 2026 Global Fraud Summit = out of 30-day window. Re-check if a fresh June operational-results article appears.

## Flags for Maria (recurring)

1. **OFAC WebFetch is dead — 15+ consecutive runs stuck at 5/8 frontier** while the RSS path carries OFAC to 6/5. Recommend dropping the OFAC URL from this scrape's source list entirely; it only wastes a fetch slot.
2. **JS-source frontier consistently exhausted between runs.** This is another effectively-zero run; the morning/RSS/gmail-monitor paths harvest the frontier before the JS scrape runs. Cadence reduction (every-other-day, or single daily run) remains worth considering.
3. CJUE remains RSS-owned — never inject via this scrape (PDF-URL dedup mismatch creates duplicates).
