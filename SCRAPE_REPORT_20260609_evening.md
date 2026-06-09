# Scrape Report — JS Sources — 2026-06-09 (scheduled)

## Outcome: 1 injected (Egmont 6/1 re-injection)

origin/main 375 → 376. Every other candidate was either already in the DB or **out of the
30-day window** (cutoff = 2026-05-10).

## Injected
- **Egmont — "Thanks Hennie Verbeek-Kusters for Exceptional Leadership and Service"** (1 Jun,
  in-window). In-scope hook = her transition Head of FIU Netherlands → **AMLA Executive Board**.
  Re-injection: this exact item was injected on 2026-06-04 (score 50) but is absent from the
  current origin/main. Borderline governance/farewell post — flagged for Maria to drop if she
  wants Egmont awareness/personnel posts out.

## Skipped — out of 30-day window (cutoff 2026-05-10)
These surfaced from the scrape as "absent from origin/main", but absence = they were already
pruned, not novelty. Per the 2026-06-09 morning correction, the 30-day gate is applied to
candidates *before* injecting:
- US Treasury sb0496 — Networks Supplying Weapons/UAV to Iran (8 May, day 32)
- US Treasury sb0492 — Iraqi Oil Official / Iran-Backed Militias (7 May, day 33)
- OFAC 20260508 — Counter Terrorism / Counter Narcotics Update (8 May, day 32)
- OFAC 20260508_33 — Non-Proliferation & Iran Designations (8 May, day 32)
- DOJ — Former Oklahoma Bank CEO Pleads Guilty to Bank Fraud (7 May, day 33)
- Wolfsberg — New Co-Chair (article dated 21 Jan; far out of window)

## Sources fetched
ACPR Communiqués/Publications (frontier 18 May SocGen, in DB) · DOJ Criminal Division
(stale snapshot, max 7 May) · OFAC Recent Actions (stale snapshot, max 8 May — known dead
via WebFetch) · US Treasury (stale snapshot, max 8 May) · Egmont (June items in DB + the
1 re-injection above) · Wolfsberg (frontier 22 May Forum, in DB) · FATF (Feb/Mar pubs, all
out of window) · Interpol (frontier 26 May, in DB) · CJUE (RSS-owned, skip). **UN SC returned
empty and Conseil de l'UE returned a stale 2017 cache** — both are JS-rendered and Chrome was
not connected on this scheduled run, so they could not be refreshed (both already in-window-
current at 5/29 / 5/28 on origin/main).

## Notes
- Chrome unavailable (scheduled run) → the two Chrome-only sources (FATF, Interpol) fell back
  to WebFetch successfully; UN SC and Conseil could not be read.
- Git: stale `.git/index.lock` (20 May) and read-only `.git` objects make normal `git add`/
  `commit` impossible — used the documented temp-index + commit-tree + direct-SHA push workflow
  (GIT_INDEX_FILE on the outputs mount) instead.
