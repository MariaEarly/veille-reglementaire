# Scrape Report — 2026-06-04 evening

**Run type:** scheduled `veille-scrape-js-sources`
**Outcome:** 4 items injected → origin/main `f8e427e..84420a7` (430 items total, +4 from 426)

## Items injected

| # | Source | Date | Title | Score |
|---|---|---|---|---|
| 1 | UN Security Council - Sanctions | 2026-05-29 | Security Council Renews Sanctions on South Sudan for One Year, Adopting Resolution 2821 (2026) | 30 |
| 2 | US Treasury - Sanctions Press | 2026-05-27 | Economic Fury Targets Iranian Maritime Extortion (PGSA, "Tehran Toll Booth") — sb0507 | 35 |
| 3 | US Treasury - Sanctions Press | 2026-05-29 | Economic Fury Targets Iranian Network Defrauding U.S. Firms to Supply Tehran's Military — sb0515 | 35 |
| 4 | US Treasury - Sanctions Press | 2026-05-19 | Economic Fury Targets Networks Generating Billions for Iran's Terrorist Regime — sb0502 | 35 |

**Note on the 3 Treasury items:** these were already identified in the 2026-06-04 *morning* scrape but skipped (per memory note) to avoid injecting too many companions in one run. This evening run picks them up. They are confirmed in-scope OFAC sanctions designations.

**Treasury date verification** (since `home.treasury.gov/news/press-releases/sb0NNN` pages WebFetch blank): used the `globalsecurity.org/wmd/library/news/iran/2026/MM/iran-YYMMDD-treasury01.htm` URL-pattern cross-reference per the 2026-05-31 precedent.
- `iran-260527-treasury01.htm` → sb0507 = 2026-05-27
- `iran-260529-treasury01.htm` → sb0515 = 2026-05-29
- `iran-260519-treasury01.htm` → sb0502 = 2026-05-19

## Items SKIPPED (judgment calls — flag for Maria)

### DOJ "Three Sentenced to Prison for Laundering Medicare Fraud Proceeds" (5/21, /opa/pr/three-sentenced-prison-laundering-medicare-fraud-proceeds)
- Scamarone, Mendez, Vazquez — $2.2M laundered through shell companies from $6.9M Medicare DME fraud, pleaded guilty to **conspiracy to commit money laundering**.
- Title literally says "Laundering Medicare Fraud Proceeds"; conduct is explicit ML.
- BUT: prosecuted by **Fraud Section + National Fraud Enforcement Division** under the Trump/Vance Task Force to Eliminate Fraud (overt political framing). No MNF prosecutor. No cross-border ML element (all domestic shell companies).
- Borderline vs the 2026-06-02 morning Georgian Citizen precedent (which was injected). Differences: Georgian Citizen had explicit **"International Money Laundering Conspiracy"** title + cross-border (to China/HK). This one is purely domestic Medicare DME fraud.
- **Decision: SKIP**, consistent with the 2026-05-27 evening precedent on omnibus Fraud Division Medicare items being out of scope. Maria — let me know if you want me to widen DOJ scope to also cover domestic Medicare-ML cases. Same call would apply to the related 5/21 "Minnesota Health Care Fraud Takedown" and 5/19 "Three Members International Criminal Organization / $2B Telemedicine".

### DOJ Compensation/Remission notices
- "Justice Department Announces Compensation Process for OneCoin Fraud Victims" — administrative victim remission notice for an old prosecuted case. Per 2026-06-03 morning AirBit Club precedent: victim-remission notices stay OUT.

### Treasury sb0520, sb0521 (out of scope)
- sb0520 = Kate Tyrrell Treasury Chief of Staff appointment (governance, not sanctions).
- sb0521 = Bessent statement before Senate Finance Committee re Trump 2027 Budget (not sanctions).

## Sources scraped

### WebFetch returned usable content
- **ACPR Communiqués**: frontier 5/18 SocGen sanction (in DB). Next item 4/27 = out of window. **0 new.**
- **ACPR Publications**: top 2 (5/22 N°50 Mutualisation, 5/21 Rapport annuel) already in DB via the generic Google-News-RSS-backed `ACPR` source. Per 2026-06-03 morning precedent: SKIP via listing scrape to avoid dups (the dedup needs a content-fingerprint, not URL-match). **0 new.**
- **DOJ Criminal Division**: listing-page-1 still anchored at 5/7 (Akhter conviction) — listing-vs-reality lag now permanent. Topical WebSearch surfaced one borderline item (above, SKIPPED). DB DOJ frontier at 5/28 (Bank Insider, MNF). **0 new injected.**
- **Wolfsberg Group**: featured 2026 Forum (5/22, in DB), Munro co-chair (1/21 = out of window, flagged in memory), stablecoin guidance + risk-based-approach + monitoring (all in DB or older). **0 new.**
- **Egmont Group**: featured 6/01 Verbeek-Kusters in DB (injected this morning); 5/26 Taipei VC, 5/25 Annual Report, 5/21 PPP, 5/20 NMFT, 5/15 Krakow, 4/30 Chair, 4/17 IMF — all in DB. **0 new.**

### WebFetch blank or stale (fallback to WebSearch + canonical-URL verification)
- **OFAC Recent Actions**: WebFetch returned empty body. DB has OFAC via RSS to 6/02. OFAC WebFetch staleness now ~9 consecutive runs at 5/8 frontier — fully dead per memory. Confirm + flag only, no inject.
- **US Treasury Sanctions Press**: individual `sb0NNN` pages WebFetch blank. Dates derived from globalsecurity.org cross-refs. **3 new injected** (sb0502, sb0507, sb0515; see table).
- **UN Security Council Sanctions**: listing JS-rendered (blank). WebSearch surfaced sc16374 South Sudan renewal (5/29) — **1 new injected**. sc16336 (1988 Sanctions Committee, Taliban) is dated 13 April 2026 = ~52 days old, out of 30-day window → SKIP.
- **Conseil de l'UE**: WebFetch returned a stale 2017-date snippet (JS-rendered). DB at 5/28 settlers + 5/26 Russia HR. WebSearch found no in-scope Conseil item newer than 5/28. **0 new.**
- **FATF/GAFI**: WebFetch returned the same stale Sep 2024 Jersey/El Salvador/Kenya MER snippet as prior runs. June plenary not yet (Mexican Presidency concludes mid-June; UK President Giles Thomson takes over July). Latest FATF outcomes still Feb 2026 plenary. **0 new.**
- **Interpol**: not WebFetched this run (Chrome unavailable per autonomous-run norm); topical WebSearch returned only the March 2026 Global Financial Fraud Threat Assessment (already in DB or older). **0 new.**

### Skipped per memory precedent
- **CJUE**: RSS-owned, the press-release listing only exposes PDF URLs that don't match the RSS canonical URL form — would create dup via md5(title+url). DB CJUE up to 6/04 via RSS. **0 new.**

## Durable observations
- **Treasury "Economic Fury" cadence catch-up**: the 3 Iran sanctions items injected this run had all been identified in the 2026-06-04 *morning* run but deferred. The Treasury Iran sanctions stream is heavy (sb0NNN runs ~3-5/week) — this evening run cleared the backlog. Going forward, the morning run should inject all in-scope items rather than deferring "too many companions" — a 30-min cadence between morning and evening doesn't change the editorial scope, and deferral creates re-verification work.
- **OFAC WebFetch dead streak**: 9+ consecutive runs at 5/8 frontier while RSS advances normally. No reason to keep WebFetch'ing this URL — wastes a request slot. Suggest dropping OFAC from the WebFetch list and relying entirely on the RSS path.
- **DOJ listing-page-1 anchored at 5/7 since at least 5/26**: now structural, not transient. Topical WebSearch (`DOJ money laundering site:justice.gov May/June 2026`) remains the only reliable surface path for fresh DOJ items.
- **Conseil clobbering pattern not observed this run**: the 5/28 settlers and 5/26 Russia HR items that were re-injected on 6/02 evening and 6/03 are still present on origin/main today. Either the clobbering pattern was a transient cron bug now fixed, or the items happened to not get clobbered this cycle. Worth one more run before declaring it resolved.

## Push log
- First push attempt: `mktemp` GIT_INDEX_FILE = 2227 bytes, tree = 20 entries (correct, not 1) — verified clean per the 2026-06-01 workaround fix.
- Push: `git push -v origin 84420a7:refs/heads/main` → `f8e427e..84420a7` landed first try, no retry needed.
- Post-push verification: `git fetch origin` → all 4 items confirmed present on origin/main (430 total items).
