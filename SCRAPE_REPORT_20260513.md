# Scrape Report - 2026-05-13 (scheduled JS sources run)

Run date: 2026-05-13T06:11:00Z
Total items in data.json after merge: 568
New items added this run (vs prior remote main HEAD): 26

## Sources scraped successfully

- ACPR Communiques (WebFetch) — parsed, deduplicated against existing
- ACPR Publications (WebFetch) — parsed, deduplicated
- DOJ Criminal Division (WebFetch) — compliance-relevant articles only
- OFAC Recent Actions (WebFetch) — sanctions / designations / general licenses
- US Treasury Sanctions Press (WebFetch) — Iran, Iraq sanctions
- Wolfsberg Group (WebFetch) — stablecoin guidance, RBA statement, monitoring statement
- Interpol (WebFetch) — financial fraud, pharma operation, cyber IP takedown
- FATF/GAFI Publications (Chrome) — Singapore/Austria/Italy/Serbia MERs, Ministerial Declaration, stablecoin & cyber-fraud reports, grey/black lists

## Sources attempted but no usable content extracted

- Council of the EU / Consilium press releases — page returned only the "About this site" block via both WebFetch and Chrome `get_page_text`. Skipped.
- UN Security Council press release index — `https://press.un.org/en/content/sc/press-release` returns 404. Skipped.
- Egmont Group news — `get_page_text` refused (page body too large / no semantic element). Skipped.
- CJUE (curia.europa.eu) — WebFetch result exceeded the inline token limit. Skipped.

## New items injected (alphabetical by source)

- **ACPR - Communiqués** — La Banque de France et l'ACPR mettent en garde le public contre un risque de fraude (2026-04-27)
- **ACPR - Communiqués** — L'ACPR et l'AMF mettent en garde le public contre plusieurs acteurs (2026-04-21)
- **ACPR - Communiqués** — Réclamations : l'ACPR constate des progrès mais alerte (2026-04-16)
- **ACPR - Communiqués** — Publication du rapport « Panorama et analyse des services d'IBAN virtuels » (2026-04-13)
- **ACPR - Publications** — N° 179 : L'assurance-vie en 2025 (2026-03-26)
- **DOJ - Criminal Division** — Federal Jury Convicts Virginia Man on Charges Relating to the Deletion of US Government Databases (2026-05-07)
- **DOJ - Criminal Division** — Member of Prolific Russian Ransomware Group Sentenced to Prison (2026-05-04)
- **GAFI/FATF** — Singapore's measures to counter money laundering (2026-05-06)
- **GAFI/FATF** — Austria's measures to counter money laundering (2026-04-30)
- **GAFI/FATF** — Italy's measures to counter money laundering (2026-04-23)
- **GAFI/FATF** — Ministerial Declaration of the FATF - April 2026 (2026-04-17)
- **GAFI/FATF** — Serbia's measures to counter money laundering (2026-04-03)
- **GAFI/FATF** — Targeted report on Stablecoins and Unhosted Wallets - P2P Transactions (2026-03-03)
- **GAFI/FATF** — Cyber-Enabled Fraud - Digitalisation and ML/TF/PF Risks (2026-02-24)
- **GAFI/FATF** — High-Risk Jurisdictions subject to a Call for Action (2026-02-13)
- **GAFI/FATF** — Jurisdictions under Increased Monitoring (2026-02-13)
- **Interpol** — Global crackdown on illicit pharmaceuticals (2026-05-07)
- **Interpol** — 45,000 malicious IP addresses taken down in international cyber operation (2026-03-13)
- **OFAC - Recent Actions** — Counter Terrorism and Counter Narcotics Designation Update, Russia removal (2026-05-08)
- **OFAC - Recent Actions** — Counter Terrorism and Iran-related Designations; Cuba Designation (2026-05-07)
- **OFAC - Recent Actions** — Issuance of Venezuela-related General License and Amended FAQ (2026-05-04)
- **OFAC - Recent Actions** — Democratic Republic of the Congo-related Designation (2026-04-30)
- **US Treasury - Sanctions Press** — Treasury hosts state insurance commissioners on private credit (2026-05-07)
- **Wolfsberg Group** — Wolfsberg Group Announces New Co-Chair (2026-04-15)
- **Wolfsberg Group** — Wolfsberg Group publishes second Statement on Effective Monitoring (2025-11-01)
- **Wolfsberg Group** — Wolfsberg Group releases its Statement on the Risk-Based Approach (2025-10-01)

## Notes

- Local repo had a stale `index.lock` that the fuse mount refused to unlink, blocking direct push from the workspace. Workaround: cloned `MariaEarly/veille-reglementaire` to `/tmp`, applied changes against the remote HEAD, committed there, and pushed (commit `a789994`). Local workspace `data.json` and report were then synced to match the pushed state.
- Dedup-by-hash logic is working — repeat scrapes against the same source pages no longer create new duplicate items.
