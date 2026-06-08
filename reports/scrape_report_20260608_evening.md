# Scrape Report — JS Sources — 2026-06-08 (evening, ~18:05 UTC)

**Result: 0 new in-scope items injected.** origin/main stable at 368 items. This run is <1h after the 17:11 UTC run (also 0-injected); frontiers identical, no source moved.

## Source-by-source
- **ACPR – Communiqués**: frontier 5/18 SocGen (Commission des sanctions, €20M blâme intermédiaire d'assurance) — in DB. Next items 4/27, 4/21 already in DB. No new.
- **ACPR – Publications**: no new (5/22 + 5/21 are dups of generic ACPR source per 6/03 precedent).
- **DOJ – Criminal Division**: listing still anchored 5/7. Topical WebSearch surfaced only: Huang 6/3 (in DB), Bank Insider 5/28 (in DB), Queens-$653M (false-positive, published 2022-02-22), Fraud-Division "$1B" omnibus (skip per precedent), AirBit remission (skip per precedent), Haidar Wells-Fargo $800K embezzlement (below-scope, USAO-NDCA), Edison-NJ internet-scam ML 51mo (below-scope, domestic USAO, no cross-border/institutional angle), TD Bank guilty plea (2024). No new in-scope.
- **OFAC – Recent Actions**: WebFetch stale at 5/8 frontier — **16+ consecutive dead runs**. DB has OFAC via RSS to 6/5. Confirm + flag only.
- **US Treasury – Sanctions Press**: frontier sb0519 6/2 Nobitex in DB. No new sb above 6/2.
- **UN Security Council**: frontier sc16374 5/29 South Sudan in DB. No new.
- **Conseil de l'UE**: frontier 5/28 Hamas/PIJ in DB. No new June canonical financial-sanction release. No clobbering observed.
- **Egmont Group**: frontier 6/4 pair (UNIDROIT art-market + FIU Day) in DB. No new.
- **Wolfsberg Group**: frontier 5/22 Forum in DB. No new.
- **FATF/GAFI**: WebFetch stale (Feb grey list snippet). No new.
- **Interpol**: no fresh in-scope (out-of-window items per precedent).
- **CJUE**: RSS-owned — skipped per standing precedent.

## Flags for Maria (reiterated)
- **Drop OFAC URL from this scrape's source list** — WebFetch dead 16+ consecutive runs; RSS path fully owns OFAC.
- **Cadence reduction** — intraday second/third runs reliably add nothing; the morning run exhausts the JS-source frontier. This run is <1h after a 0-item run and found nothing, reinforcing the case for reducing run frequency.
- **Treasury lead-verification rule** (from 17:11 run): canonical URL prefix `jy####` = Biden-era/out-of-window; only `sb0###` is current. Combined with the globalsecurity `YYMMDD` cross-ref for date.

No data.json change. Report-only push.
