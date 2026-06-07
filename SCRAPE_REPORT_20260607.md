# Scrape Report — JS Sources — 2026-06-07 (morning)

**Task:** `veille-scrape-js-sources` | **Result: 0 new items injected.** origin/main unchanged at 375 items (window cutoff 2026-05-08).

## Outcome
No genuinely-new, in-scope, in-window item found. Consistent with the established cadence (the 06h/12h/18h cron + gmail monitor keep the 30-day window fully harvested; typical run = 0–1 new items). This is now the 6th effectively-zero run in ~12 days.

## Sources fetched (WebFetch returned usable content)
- **ACPR Communiqués** — frontier = SocGen sanction 18 May (already in origin/main). All other listed items (BdF/ACPR fraud-usurpation 27 Apr, ACPR/AMF mise-en-garde 21 Apr, IBAN-virtuels/Tracfin report 13 Apr) are **out of the 30-day window** (cutoff 2026-05-08).
- **ACPR Publications** — LCB-FT webinar replay (2 Mar) and LCB-FT transmission-de-fonds control bilan (9 Dec 2025) both **out of window**. (Also: per prior precedent, ACPR Publications items tend to duplicate the generic RSS-backed `ACPR` source.)
- **DOJ Criminal Division** — listing page-1 still anchored 7 May (permanent lag). Bank-fraud Oklahoma (5/7) already in DB; Russian-ransomware sentencing (5/4) out of window and already injected back on 5/24. Topical search surfaced no new in-window in-scope ML/sanctions item.
- **OFAC Recent Actions** — WebFetch **stale-cached at the 8 May frontier for 14+ consecutive runs** (RSS path owns OFAC and is current). Nothing to inject; per standing precedent OFAC is never injected via this scrape.
- **US Treasury Sanctions Press** — WebFetch frontier likewise stale at 7–8 May ("Economic Fury" Iran items sb0496 5/8, sb0492 5/7). These are stale-cache artifacts that have naturally aged out of the window, not new items — skipped.
- **Wolfsberg** — homepage fetchable this run; newest = 2026 Wolfsberg Forum (5/22), already in origin/main.
- **CJUE** — curia listing exposes two in-scope cases, **case 74/2026 "Across Fiduciaria" (AML / beneficial ownership, 21 May)** and **case 73/2026 "freezing of assets in trust" (restrictive measures, 21 May)**. Both **skipped: CJUE is RSS-owned** (origin/main carries `CJUE - Cour de Justice UE`, source_type=rss; case 74 already present via RSS). Injecting the PDF-URL form would create duplicates.

## Sources NOT reachable this run (no Chrome browser connected)
JS-rendered / blank-to-WebFetch: **Egmont** (JS shell redirect), **UN Security Council** (blank), **Conseil de l'UE** (returned a stale 2017 cache via WebFetch; individual pages JS-rendered), **FATF/GAFI** (stale 2024 snippet), **Interpol** (Chrome-only, listing not fetchable). Chrome was not connected on this autonomous run, so these could not be verified live. No in-scope leads surfaced for them via the other sources.

## Flags for Maria
1. **OFAC + Treasury WebFetch are effectively dead** — both stuck at the 7–8 May stale cache (OFAC 14+ runs). Recommend dropping the OFAC URL from this scrape's source list entirely; the RSS path owns it and is current. Treasury sanctions items likewise arrive via RSS.
2. **Cadence** — 6th near-zero run in ~12 days. The intraday/evening JS scrape reliably adds nothing once the morning cron has run; a candidate for reducing to once-daily or every-other-day.
3. **Local clone still degraded** — stale `.git/index.lock` + `refs/heads/main.lock` (20 May) remain un-removable in the sandbox ("Operation not permitted"); pushes go via the temp-index/commit-tree/direct-SHA workaround. Worth a manual lock-clear + reconcile when convenient.
4. **No-live-page-read caveat** applies to Egmont/UN SC/Conseil/FATF/Interpol this run (Chrome unavailable).

_Generated autonomously; no clarifying questions possible during a scheduled run._
