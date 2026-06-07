# Scrape Report — 2026-06-07 (evening)

**Run:** scheduled `veille-scrape-js-sources`
**Result:** 2 items injected. origin/main 368 → 370 items. Push `4060412..af5d583` (temp-index, tree 28 entries).

## Injected (both new, both Egmont, dated 2026-06-04)

1. **Egmont Group Contributes to UNIDROIT Workshop on Art Market Integrity** (score 35, `autorite_intl`, action_class=info).
   Substantive AML content: art/antiquities market money-laundering and illicit-flow risks, FIU cross-border cooperation on cultural-property-trafficking financial flows. Clear in-scope. Date confirmed via `og:image` path `2026/06/...` and homepage dateline.
2. **Egmont Group Marks International FIU Day on 9 June** (score 30, `autorite_intl`, action_class=info).
   **Judgment call / borderline** — commemorative awareness post, but centers on the global FIU network's AML/CFT mission and is consistent with the DB's established pattern of keeping Egmont institutional posts (annual report, conferences, governance). Flagged for Maria to remove if she wants Egmont awareness posts out of scope.

## Source-by-source (all others exhausted at the same frontier already in DB)

- **ACPR Communiqués:** frontier 5/18 (SocGen €20M intermédiaire d'assurance). Nothing newer. ✓
- **DOJ Criminal Division:** listing page-1 still anchored **5/7** (permanent lag). Topical search surfaced only items already in DB (Huang 6/3) or out-of-scope/false-positive:
  - "Queens Man $653M Money Laundering Conspiracy" — **false positive, published_time = 2022-02-22** (4 years old). Skipped. Re-confirms: always read `meta-article:published_time`, never trust the topical-search summary's date.
  - NJ "$9M PPP fraud + ML proceeds" forfeiture — domestic PPP, skip per domestic-fraud precedent.
  - Haidar (Wells Fargo $800K embezzlement, 6/1, USAO-NDCA) — below-scope (routine local embezzlement, no MNF/cross-border). Skip per 6/05 precedent.
  - Fraud Division "$1B" omnibus + AirBit victim-remission — skip per standing precedents.
- **OFAC Recent Actions:** WebFetch **still dead** — frontier stuck at **5/8** (now ~14 consecutive runs) while DB has OFAC via RSS to 6/05. **Reiterated flag: drop the OFAC URL from this scrape's source list; the RSS path owns it and this fetch slot is wasted.**
- **US Treasury Sanctions Press:** listing frontier 5/9 (sb0497 remarks; sb0496 5/8 Iran weapons/UAV "Economic Fury"; sb0492 5/7 Iraqi oil/Iran militias) — both **older than DB's Treasury frontier (6/02)** and at/over the 30-day pruning boundary (5/7 = day 31, 5/8 = day 30). They'd be pruned almost immediately, so **not injected** (backfill of imminently-prunable items adds no value). Flagged in case Maria wants the edge backfilled. DB already holds 7 newer "Economic Fury" items (5/28–6/02).
- **UN Security Council:** frontier sc16374 (5/29 South Sudan). Search surfaced nothing newer than 5/21 indexed (sc16336 4/13, sc16313 3/10 both old). ✓
- **Egmont:** see Injected above. (The 6/1 Verbeek-Kusters, 5/26 Vice-Chair, 5/25 Annual Report, 5/21 PPP all already in DB.)
- **Wolfsberg Group:** homepage returned content this run (was blank on 6/04–6/06). Newest in-window = 2026 Forum (5/22, in DB). Munro co-chair (Jan), Second Statement on Effective Monitoring (4/20), stablecoin guidance (2025) all out-of-window. ✓
- **FATF/GAFI:** Feb 2026 grey list still the frontier; no June plenary publication yet (June statements typically land late-June). ✓
- **Interpol:** no fresh in-scope item. Operation Shadow Storm (Mar launch), RED CARD 2.0 (Dec–Jan), Global Fraud Threat Assessment (Mar) all out-of-window. DB frontier 5/18. ✓
- **Conseil de l'UE:** no new June canonical financial-sanction press release. Crimea-regime extension is a renewal, not a new designation. ✓ (Clobbering pattern not observed — 5/28 settlers + 5/26 Russia HR still present.)
- **CJUE:** RSS-owned, skipped (frontier 6/04 via RSS).

## Standing flags reiterated to Maria
- **Drop OFAC URL** from this scrape (14+ dead WebFetch runs; RSS covers it).
- **DOJ listing-page-1 lag is permanent** — topical WebSearch + `published_time` verification remains the only reliable DOJ path.
- **Cadence:** intraday second runs continue to add ~0 net new beyond Egmont's daily institutional posts; consider whether daily JS-scrape frequency is worth the cost.
