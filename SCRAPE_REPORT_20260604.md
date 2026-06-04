# Scrape Report — 2026-06-04

**Run type:** scheduled `veille-scrape-js-sources`
**Window:** 30 days back from 2026-06-04 (i.e., ≥ 2026-05-05)
**Push:** `6be24f0..1d6198a` (3 items injected, 425 total)

---

## Injections (3)

| Source | Date | Title | Score | Notes |
|---|---|---|---|---|
| Egmont Group | 2026-06-01 | Egmont Group Thanks Hennie Verbeek-Kusters for Exceptional Leadership and Service | 50 | She transitioned from Head of FIU NL → **AMLA Executive board** — that's the in-scope hook (not just a farewell); also covers her work on the FIU.NET-style secure exchange platform supporting 182 FIUs. Verified `meta-article:modified_time = 2026-06-01T21:02:33Z` on the article page. |
| US Treasury — Sanctions Press | 2026-05-28 | Economic Fury Targets Illicit Oil Revenue Fueling Iran's Military (`sb0510`) | 35 | Companion to OFAC Iran-related designations already in DB; per 2026-05-31 precedent (Treasury parent + OFAC child = both kept). Date sourced from `globalsecurity.org/.../iran-260528-treasury01.htm` because Treasury individual `sb0NNN` pages WebFetch blank. |
| US Treasury — Sanctions Press | 2026-06-02 | Economic Fury Targets Iran's Largest Digital Asset Exchange for Terror Finance and Sanctions Evasion (`sb0519`) | 35 | **Nobitex** + 3 other Iranian crypto exchanges — high editorial value for Early Brief (crypto + sanctions evasion + CBI stablecoin laundering). Companion to the 6/2 OFAC Iran-related action already in DB. |

---

## Skipped — out of window

- **DOJ Tren de Aragua ATM Jackpotting Indictment** (USAO-NE) — surfaced via topical WebSearch with no clear date; the article-detail page shows `published_time = 2025-12-18` → **6 months old**, well past the 30-day window. (Article was *updated* 2026-03-13, which is what some indexers were keying on.)
- **DOJ TD Bank Insider — Oscar Marcel Nunez-Flores** (OPA `/opa/pr/td-bank-insider-pleads-guilty-facilitating-colombian-atm-money-laundering-scheme`) — `published_time = 2026-01-21` → **4.5 months old**. NOT the same person as the 5/28 "Bank Insider Pleads Guilty to Facilitating Fraud Schemes at Two Financial Institutions" already in DB.

Both confirm the "always open the page and read `meta-article:published_time` — never trust the WebSearch summary's date" rule from 2026-06-02 evening.

---

## Skipped — out of scope (flagged for Maria)

- **Interpol 5/26 "Over 3,300 illegal firearms, 56 tonnes of drugs seized in Operation in the Americas"** — same Operation Orca XI cluster already SKIPPED on 2026-06-02 evening (firearms/drugs op headline; the financial-crime element is incidental).
- **Interpol 5/20 "Convenes Europe's top police over evolving transnational organized crime"** — already SKIPPED on prior runs (governance/policing conference, not a financial-crime operation or report).

## Skipped — already covered by another source (deduplication)

- **ACPR Publications 5/22 "N°50 Mutualisation intercohortes des risques dans les contrats d'assurance-vie"** + 5/21 "Rapport annuel ACPR 2025" — already in DB under the generic `ACPR` source via Google-News RSS. Per 2026-06-03 precedent on the `ACPR - Publications` source: the URL-based dedup misses these because the listing scrape and the RSS use different URLs; skipping by content fingerprint instead. If Maria wants `ACPR - Publications` populated separately, the dedup needs a content-fingerprint, not URL-match.
- **Treasury Press parents for `sb0507` (5/27 Iranian Maritime Extortion), `sb0502` (Networks Generating Billions), `sb0515` (5/29 Iran Network Defrauding U.S. Firms)** — all OFAC-companion items. Per 2026-05-31 precedent these could be injected, but to avoid over-injection on a single run I kept only the two most editorially distinctive ones (sb0510 oil + sb0519 crypto exchange). Flagging for Maria's call: do you want every Treasury "Economic Fury" press release injected as a parent, or only the ones with distinct narrative angles?

---

## No new items

- **ACPR Communiqués** — frontier 5/18 (SocGen sanction); page-1 has nothing between 5/18 and today.
- **DOJ Criminal Division** — listing page-1 frontier still anchored 5/7 (Akhter, Seibel, etc.) for the **8th consecutive run**. Permanent lag; topical WebSearch is the only reliable surface path now. Today's topical searches surfaced only out-of-window items (TD Bank Insider Nunez 1/21, Tren de Aragua Indictment 12/18).
- **OFAC Recent Actions** — WebFetch frontier still 5/8 for the **8th+ consecutive run**. Fully dead via this scrape; OFAC RSS in DB is current to 6/2.
- **UN Security Council** — WebFetch returns blank as usual. No fresh in-scope items surfaced via WebSearch.
- **FATF** — WebFetch returns the stale Sep-2024 snippet (Jersey/El Salvador/Kenya MERs). No new plenary output — June 2026 plenary not yet held.
- **Wolfsberg** — frontier on homepage = 5/22 Wolfsberg Forum (in DB); next item Munro co-chair is the 2026-01-21 pinned/featured item (out of window — same precedent as 2026-05-24 and 2026-06-02 evening: always open the article page and check the bare YYYY-MM-DD before treating any Wolfsberg homepage link as new).
- **CJUE** — RSS-owned; skipped here per 2026-05-21 precedent to avoid PDF-URL duplicates of items already entering via the `CJUE - Cour de Justice UE` RSS feed.
- **Conseil de l'UE** — WebFetch returns truncated 2017-era output. WebSearch surfaced the 6/2 "Hungary obtained removal of Patriarch Kirill from the 20th sanctions package list" sub-detail, but no canonical Consilium URL for a stand-alone 6/2 press release was found (the underlying 20th package itself dates to 2026-04-23 = out of window, already correctly skipped on prior runs).

---

## Operational notes

- Push pattern (`mktemp` GIT_INDEX_FILE → `read-tree origin/main` → blob/tree/commit-tree → `git push -v <SHA>:refs/heads/main`) worked on the second attempt: first push 413a61f was rejected non-fast-forward (origin moved 425 → 422 items between read and push — pruning event), then re-fetched, re-injected onto the new origin/main, and `6be24f0..1d6198a` landed cleanly. Index size 2139 bytes, tree 19 entries — both verified before push.
- `tmp_obj_*` "Operation not permitted" warnings during hash-object/commit-tree are cosmetic; objects exist and push succeeds.
- The stale `.git/index.lock` and `.git/refs/heads/main.lock` from 2026-05-20 are still present and still un-removable; the temp-index workaround sidesteps both.

---

## Questions for Maria

1. **Treasury "Economic Fury" omnibus** — there are ~5 "Economic Fury" press releases in May-June 2026 that are OFAC-companion sanctions parents. Want them all injected (per the 2026-05-31 companion precedent), or only the editorially distinctive ones (current behavior)?
2. **ACPR - Publications source** — keeps being dup-skipped via the generic `ACPR` RSS source. Worth wiring content-fingerprint dedup, or kill this source entirely?
3. **JS-scrape cadence** — DOJ listing-page-1 lag is now permanent, OFAC WebFetch is fully dead, FATF/UN SC/Conseil all return blank/stale to WebFetch. The "value-add" of this scheduled run is almost entirely from topical WebSearches now. Worth rethinking the source mix?
