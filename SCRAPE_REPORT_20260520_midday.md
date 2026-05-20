# Scrape Report — JS Sources (Scheduled) — 2026-05-20 (midday run)

**Run:** scheduled `veille-scrape-js-sources` · autonomous (user not present) · ~12:08 UTC
**Result:** 1 new article injected · base = latest `origin/main` (559 items) → 560 items
**Note:** This is the 12:00 UTC cron slot. The 06:50 UTC run already did a thorough pass earlier today, so almost everything recent was already in the DB.

## New article added

| Score | Source | Category | Date | Title |
|------|--------|----------|------|-------|
| 35 | Interpol | autorite_intl | 2026-05-18 | 201 arrests in first-of-its-kind cybercrime operation in MENA region (Operation Ramz) |

## Sources checked

**WebFetch (Group 1):**
- ACPR Communiqués — ✅ checked. SocGen sanction (18 May), BdF/ACPR fraud-usurpation warning (27 Apr) and ACPR/AMF "plusieurs acteurs" warning (21 Apr) all already in DB. The ACPR–Tracfin "IBAN virtuels / blanchiment" report is genuinely new but dated **13 Apr 2026 — outside the 30-day window** (DB cutoff is 2026-04-20), so it would be pruned immediately. Skipped.
- ACPR Publications — ✅ checked. No in-window in-scope items (LCB-FT webinar 2 Mar, transmission-de-fonds bilan Dec, etc. all pre-window; insurance/climate publications out of scope).
- DOJ Criminal Division — ✅ checked. Only financial-crime item (Oklahoma bank fraud, 7 May) already in DB. Cyber/ransomware/smuggling/drugs/violent-crime items skipped as out of scope.
- OFAC Recent Actions — ✅ checked. All actions on the live page (through 20260508) already in DB; DB already extends to 20260518. Nothing new.
- US Treasury Sanctions Press — ✅ checked. "Economic Fury" sanctions items (sb0492, sb0496) already in DB. Non-sanctions items (refunding, TBAC, commencement remarks) out of scope.
- Wolfsberg Group — ✅ checked. All current news items already in DB.
- Egmont Group — ✅ checked (WebSearch; site is JS-redirect). All May items already in DB (Krakow intersessional 15 May, Luxembourg 30th anniversary 8 May, World Bank/IMF 7 May, Chair Highlights 6 May). Nothing new.
- CJUE (curia) — ✅ checked. Press-releases page is nav/JS-heavy with no AML/sanctions/financial-compliance cases listed (consistent with full history). Nothing added.

**JS-rendered (WebFetch empty/blocked → WebSearch + targeted WebFetch fallback; no Chrome connected):**
- Conseil de l'UE — ✅ Syria (18 May) and Ukrainian-children (11 May) already in DB; the EU 20th Russia sanctions package (23 Apr) already in DB; Myanmar extension (27 Apr) already in DB. The Cyber-attacks sanctions item (16 Mar) is new but **outside the 30-day window** — skipped.
- UN Security Council — ⚠️ press.un.org is bot-protected (JS "Client Challenge"); could not confirm exact dates. Candidate committee press releases (1591 Sudan; 1988 amendments) map to the Feb–mid-Apr timeframe per WebSearch — i.e. **outside the window / already in DB** (DB already holds UN items through 7 May). When dates couldn't be confirmed as in-window, items were skipped (per task rule "when in doubt, skip").
- FATF/GAFI — ✅ Singapore Mutual Evaluation (6 May) already in DB. Nothing new.
- Interpol — ✅ **1 new (Operation Ramz, 18 May).** See judgment note below. Other Interpol items (financial-fraud threat assessment, Africa online-scams op, illicit-pharma crackdown, UNODC summit) already in DB.

## Notes / autonomous decisions

- **Operation Ramz — borderline scope call (included).** INTERPOL classifies it primarily as a *cybercrime* operation (phishing/malware), which on its own would be out of scope. It was included because the fraud dimension is central — investment/trading-platform fraud, 3,867 financially-defrauded victims, seized banking data — and the DB already contains directly comparable INTERPOL fraud/scam operations (e.g. the Africa online-scams operation) and even an illicit-pharma crackdown, so this clears the DB's de facto bar. If Maria considers pure-cyber takedowns out of scope, this single item (hash `f16b99be5465`) is easy to remove. Score: 35 (fraud +20, "bank" +5, autorite_intl +10).
- **30-day window is the binding constraint this run.** Several genuinely-new, genuinely-relevant items (ACPR–Tracfin IBAN virtuels report 13 Apr; EU cyber-attacks sanctions 16 Mar) were skipped solely because they fall before the DB's 2026-04-20 prune cutoff and would be removed on the next ingest. Flagging the ACPR IBAN-virtuels/blanchiment report in particular as a high-relevance item that the aggregator missed during its publication window.
- **Git state:** the working-directory mount still blocks file deletion (`unlink: Operation not permitted`), leaving stale `.git/HEAD.lock` and `.git/index.lock`, and the local HEAD is a stale orphan from the morning run. Worked around it by basing this commit on the latest `origin/main` (which the Actions cron + gmail monitor had advanced to `3a330c4`) using a temporary git index, and pushing the commit SHA directly to `refs/heads/main`. Built on the remote's data.json (559 items) so the cron's intervening updates are preserved.
- Backup of pre-injection data.json written to `data.json.bak.scheduled_scrape_js_<ts>`.
