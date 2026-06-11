# Scrape Report — JS Sources — 2026-06-11

**Run type:** scheduled `veille-scrape-js-sources` (autonomous)
**Outcome:** **0 injected** — frontier exhausted, no in-window, in-scope, non-duplicate items.
**Baseline:** `origin/main` = 386 items (oldest 2026-05-12). Window gate cutoff = today − 30d = **2026-05-12**.

## Method note
Applied the 30-day window gate (`published >= 2026-05-12`) to every candidate **before**
dedup/inject — the standing correction to the early-June over-injection churn. A candidate's
absence from `origin/main` is NOT evidence of novelty when it predates the cutoff (it was
pruned). Dedup verified by URL/title against the fresh `origin/main` snapshot, not local HEAD.

## Per-source results

| Source | Frontier found (WebFetch) | Status |
|---|---|---|
| ACPR – Communiqués | SocGen sanction **18 May** (newest); BdF/ACPR fraude-usurpation 27 Apr | SocGen already in DB; 27 Apr out of window → **skip** |
| ACPR – Publications | N°50 Mutualisation 22 May; Rapport annuel 21 May (newest two) | both in DB; rest ≤ 31 Mar out of window → **skip** |
| DOJ – Criminal Division | WebFetch returned **stale snapshot** (newest item May 7) | DB already holds DOJ to **6/03** (intl money-laundering org); snapshot behind DB → **skip** |
| OFAC – Recent Actions | WebFetch dead/empty (recurring, 19+ runs) | RSS owns OFAC, current to **6/10** in DB → **skip** |
| US Treasury – Sanctions Press | WebFetch empty (JS-rendered) | RSS/press owns, current to 6/02 → **skip** |
| UN Security Council | WebFetch empty (JS-rendered) | DB current to 5/29 → **skip** |
| Conseil de l'UE | WebFetch returned **2017 archive** (stale render) | DB current to 5/28 → **skip** |
| Egmont Group | WebFetch JS redirect (Chrome-only) | DB current to 6/04 → **skip** |
| Wolfsberg / CJUE / FATF / Interpol | RSS-owned; DB current (CJUE 6/04, Wolfsberg 5/22, Interpol 5/18) | no new in-window in-scope → **skip** |

## Operational flags for Maria
- **Git locks persist (unremovable).** `.git/index.lock` + `.git/HEAD.lock` (dated 20 May) are
  permission-denied on `rm` ("Operation not permitted"), so normal `git add`/`commit` fail and
  the local clone is diverged (1 ahead / 228 behind `origin/main`). The standing workaround still
  works: fresh `GIT_INDEX_FILE` on the outputs mount → `read-tree origin/main` → `commit-tree` →
  direct-SHA `git push -v`. This run's report was pushed that way. **Recommend** clearing the
  lock files host-side so routine git works again.
- **Drop the OFAC URL from this scrape's source list** (reiterated, now ~19 runs): OFAC WebFetch
  returns empty/stale every run; the RSS path owns OFAC and is current. Pure wasted fetch slot.
- **Hard-code the `published >= today−30d` gate into `scraper.py`** rather than relying on
  per-run discipline. The stale DOJ/Treasury/OFAC/Consilium WebFetch snapshots are permanent
  out-of-window traps (their newest items are always ~30d old or older).
- **Cadence:** the JS frontier is reliably exhausted by RSS, which runs ahead. Consider dropping
  to once-daily — the JS scrape has produced 0 net injections for the last several runs.
