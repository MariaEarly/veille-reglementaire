# Scrape Report — JS Sources — 2026-06-10

**Run:** scheduled `veille-scrape-js-sources` (autonomous)
**Items before:** 376 → **after:** 392 (**+16 injected**, 2 skipped as already present)

## Sources fetched (WebFetch)
| Source | Status | Notes |
|---|---|---|
| ACPR Communiqués | OK | 2 new (fraude/usurpation, IBAN virtuels-LCB-FT), 1 lower-relevance warning, SocGen sanction already present |
| ACPR Publications | OK | 2 new (replay webinaire LCB-FT, bilan LCB-FT transmission de fonds) |
| DOJ Criminal Division | OK | 1 new (Oklahoma bank fraud); ransomware/drug/smuggling items skipped (out of AML/sanctions scope) |
| US Treasury Sanctions Press | OK | 2 new (Iran UAV networks, Iraqi oil official/Iran-backed militias) |
| OFAC Recent Actions | OK | 3 new (May 7–8 designations) |
| Wolfsberg Group | OK | 2026 Forum already present; no new compliance items |
| CJUE (curia) | OK | 1 new (C-483/23 T Trust – freezing of assets in trust); other judgments off-topic |
| GAFI/FATF | OK | 2 new (stablecoins/unhosted wallets, cyber-enabled fraud) |
| Interpol | OK | 2 new (INTERPOL-UNODC fraud summit, financial fraud threat report) |
| UN Security Council | EMPTY | Returned no content via WebFetch |
| Egmont Group | BLOCKED | JS-gated ("Javascript is required") — needs Chrome |
| Conseil de l'UE (Consilium) | STALE | WebFetch returns client-rendered shell (old 2017 dates) — needs Chrome |

## Group 2 (Chrome-only) note
No Chrome browser is connected to this session, so the Chrome fallback path was unavailable. FATF and Interpol succeeded via WebFetch (no 403 this run), so they were captured anyway. **Egmont, Consilium, and UN Security Council could not be scraped** and should be retried when Chrome is connected.

## Filtering
Applied compliance scope: kept AML/LCB-FT, sanctions, money laundering, fraud, asset freeze, designations, FATF/financial-crime items. Skipped out-of-scope DOJ items (drugs, human smuggling, violent crime, pure ransomware) and off-topic CJUE judgments.

## Dedup
Skipped by exact URL/hash match: ACPR SocGen sanction, Wolfsberg 2026 Forum. Dedup checked **both** hash and URL to avoid cross-source duplicates.

## Data quality note
7 pre-existing duplicate normalized URLs exist in data.json from prior runs (EBA ×2, Consilium ×3, OFAC 20260511, Treasury sb0498). Not introduced by this run; left unchanged (out of scrape scope).
