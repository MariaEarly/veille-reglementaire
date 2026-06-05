# Scrape Report — 2026-06-05 (morning)

**Run type:** scheduled JS-source scrape
**Items injected:** 3
**DB size:** 426 → 429
**Commit:** `cb33bf5` (chore: scrape JS sources [scheduled])

## Injected

| # | Source | Date | Title | Score | Notes |
|---|--------|------|-------|-------|-------|
| 1 | Conseil de l'UE | 2026-05-28 | Hamas and the Palestinian Islamic Jihad: Council expands legal framework + 10 individuals added to sanctions list | 32 | Asset freeze + travel ban; targets Hamas Political Bureau members. EU restrictive measures. Canonical URL form (dedup-safe). WebFetch returned blank — verified via WebSearch provenance per 2026-05-21 precedent. |
| 2 | DOJ - Criminal Division | 2026-06-02 | Aspiration Partners Co-Founder Sentenced to Prison for $248M Scheme to Defraud Investors and Lenders | 35 | Joseph Sanberg (fintech co-founder), 14 years for wire fraud (no ML charge, only 2 counts wire fraud). Prosecuted by Criminal Division **Fraud Section** + USAO C.D. Cal. **Judgment call** — Fraud Section (not MNF) per the 2026-05-27 evening "political-framing" precedent, but defendant is fintech/financial-sector and victims are lenders/investors; press release has no Trump/Vance Task Force framing. Major scale ($248M) tipped it IN. |
| 3 | DOJ - Criminal Division | 2026-05-18 | California Man Sentenced to 15 Years in Prison for Money Laundering, False Testimony | 35 | Mohammed Adi, 15yr, MNF prosecution. Bulk-cash laundering for marijuana drug-trafficking org with CTR-structuring across multiple bank accounts. **Backfill** (older than DB DOJ frontier of 5/28) — clean MNF + ML + financial-system-abuse fits the same precedent slot as Adi/Saab/Lindberg etc. |

## Skipped (verified candidates)

- **DOJ "Leader of Colombian Money Laundering Org" (Nunez Daza, Luky)** — `meta-article:published_time = 2025-11-26` (6 months old, false-positive trap as noted in memory). Skipped.
- **DOJ Tamim Haidar Wells Fargo embezzlement (June 1, 2026 per search summary)** — couldn't verify a 2026 OPA URL; only USAO-NDCA URLs surfaced and search summary date may be unreliable. Skipped pending canonical URL.
- **DOJ "Final of Four Conspirators / darknet counterfeit pills" (5/27)** — counterfeit-pills / dark-web drug trafficking, no ML angle; out of scope per prior precedent.
- **DOJ TD Bank Pleads Guilty $1.8B** — that's the 2024 settlement (already historical); not a fresh release.
- **Treasury sb0520 / sb0521 / sb0522** — all governance/budget items (Bessent statements to House Ways & Means, Senate Finance Committee; Tyrrell Chief-of-Staff appointment per memory). Out of scope per 2026-06-04 evening precedent.
- **No Treasury sb0523+** found via search (none exists yet).
- **Conseil 5/18 Syria al-Assad regime renewal** — already in DB.
- **Conseil 5/11 Syria EU-Syria Cooperation Agreement** — financial sanctions LIFTING (was injected previously via Syria 5/18 framework decision; same regime).
- **Conseil 5/29 "Forward look: 1-14 June 2026"** — meta/agenda press release, not a sanction.
- **Conseil 6/1 Justice and Home Affairs Council briefing** — migration/asylum focus per Conseil-migration-skip precedent.
- **OFAC** — WebFetch frontier still **5/8** (now 10+ consecutive runs dead) while DB advances via RSS to 6/02. Recommend dropping OFAC URL from this scrape entirely per 2026-06-04 evening flag — RSS owns it.
- **CJUE** — skipped (RSS-owned per durable precedent).
- **FATF** — WebFetch returned stale Sep-2024 snippet (Jersey/El Salvador/Kenya MERs). DB frontier 5/6 Singapore — no fresh in-scope items.
- **UN SC** — WebFetch blank as expected. DB frontier sc16374 (5/29 South Sudan) — no fresher in-scope item visible via WebSearch.
- **Wolfsberg** — WebFetch returned only static homepage CBDDQ-themed content (no fresh news listing). DB frontier 5/22 Forum — no fresher item.
- **Egmont** — WebFetch blank/redirect as expected. DB frontier 6/01 Verbeek-Kusters (already in).
- **Interpol** — DB frontier 5/18 cybercrime MENA; 5/26 firearms/drugs Americas and 5/20 European Conference both stay SKIPPED per editorial precedent.
- **ACPR Communiqués** — frontier 5/18 SocGen (already in).
- **ACPR Publications** — frontier 5/22 N°50 (covered by generic ACPR source).

## Source frontier states

| Source | DB Frontier | Live | Status |
|---|---|---|---|
| ACPR Communiqués | 5/18 SocGen | 5/18 SocGen | Aligned |
| ACPR Publications | 5/22 N°50 (dup-covered) | 5/22 N°50 | Aligned |
| DOJ Criminal Division | 5/28 Bank Insider (now 6/2 Aspiration after this run) | listing-page-1 still anchored 5/7 (lag) | Pattern persists; topical search is the only reliable surface |
| OFAC Recent Actions | 6/02 (RSS path) | 5/8 (WebFetch dead 10+ runs) | **Drop from this scrape's URL list — RSS-owned** |
| Treasury Press | 6/02 sb0519 | sb0522 (governance, OOS) | Aligned for sanctions sb0NNN |
| UN SC | 5/29 sc16374 | (blank) | Aligned |
| Wolfsberg | 5/22 Forum | (static homepage only) | Aligned |
| Egmont | 6/01 Verbeek-Kusters | (blank/redirect) | Aligned |
| Conseil de l'UE | 5/28 Settlers + 5/28 Hamas/PIJ (now) | 5/28 Hamas/PIJ verified | Aligned |
| FATF | 5/6 Singapore | (stale 2024 snippet) | Aligned |
| Interpol | 5/18 cybercrime | 5/26 firearms (OOS), 5/20 conf (OOS) | Aligned |
| CJUE | 6/04 (via RSS) | RSS-owned | Skip |

## Flags for Maria

1. **Aspiration Sanberg — Fraud-Section judgment call.** Injected as a borderline Fraud-Section case because defendant is fintech founder and scale is $248M, no political framing in the release. If you want to tighten DOJ Fraud-Section scope to MNF-only (excluding even major fintech fraud), let me know — I'll re-skip future analogues.
2. **OFAC WebFetch fully dead (10+ consecutive runs at 5/8 frontier).** Strong recommend removing the OFAC URL from this scrape's source list — the RSS path covers it. Saves analysis time.
3. **Conseil clobbering pattern not observed this run** (3rd consecutive non-clobber day). Earlier 5/28 Settlers + 5/26 Russia HR + today's 5/28 Hamas/PIJ all stable on origin/main. Likely resolved.
4. **Origin/main moved between fetch and push** (3 cron commits landed in the gap — email-newsletter, gmail-monitor, veille update). The push still fast-forwarded cleanly because the read-tree happened to be on the new tip; flagging because under different timing the push would have needed re-fetch + re-inject.
