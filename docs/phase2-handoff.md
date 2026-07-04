# Phase 2 Handoff — Livestock Market Analyzer

**Status as of 2026-07-04: Phase 1 (data pipeline) complete and verified.**
Repo: `odellnoah-svg/livestock-market-analyzer` (public, GitHub Pages enabled, deploy from main/root).

## What exists and works

- **500,391 normalized rows** across 120 files: 21 USDA report slugs, 2021–2026
  (Salem AR starts 2023, Four State Exeter starts 2025 — those reports didn't
  exist earlier). Slug 3232 (national summary) was removed: it was a text/PDF
  report USDA discontinued 2026-04-13, never a structured MARS series.
- **GitHub Actions sync** (`.github/workflows/sync.yml`): auto `update` every
  Friday 18:00 UTC; manual dispatch offers update / discover / backfill /
  renormalize. Secret `MARS_API_KEY` is configured.
- **Correction-safe updates**: update mode drops all existing records inside
  the fetched window and replaces them, so USDA revisions overwrite stale rows.
- **raw_cache/** holds gzipped raw API responses; `renormalize` mode rebuilds
  all of data/ from cache with zero API calls. Any normalizer change = edit
  script → commit → run renormalize. Never re-run backfill.
- **Data quality (audited on real files)**: zero null weights/prices/dates,
  zero duplicates, all rows Final, class taxonomy stable 2021→2026.
  Replacement-cattle rows fully populate `age` and `preg` (bred stage) with
  per-unit prices → Female Value Deviation is computable from public data.
- **Narratives**: `data/{group}/{slug}_{year}_narratives.json`, one entry per
  sale date — intended input for the Phase 4 AI layer.

## Data access for Claude sessions

- `https://raw.githubusercontent.com/odellnoah-svg/livestock-market-analyzer/main/...`
  is reachable from Claude's sandbox (data/index.json is the manifest).
  The GitHub Pages domain `odellnoah-svg.github.io` is NOT reachable.
- GitHub API works but rate-limits quickly unauthenticated; prefer raw URLs.
- Script edits are delivered as full-file paste-overs via the GitHub web editor
  (Noah's preferred workflow; it has worked reliably).

## Normalized schema (v2, verified against live USDA payloads)

date, slug_id, market_group, species (per-row: cattle/sheep/goat), tier
(tradeable|context), commodity (Feeder Cattle / Slaughter Goats / Replacement
Cattle ...), cls (Steers, Kids, Nannies/Does, Bred Cows ...), frame, muscle,
quality, dressing, yield_grade, age, preg, calf_wt_est, wt_min/max/avg,
wt_break_lo/hi (USDA standardized weight buckets — use these for indexes),
price_min/max/avg, basis (per_cwt | per_head | "per unit" | "per family"),
head, receipts, lot_desc, wt_collect, final.

Known cosmetic debt: normalize "per unit"→per_unit, "per family"→per_family
on the next script touch. Bred stock/pairs/families price per unit ($/hd
equivalent) — critical for IV math.

## Phase 2 spec (next session)

Standalone HTML app on GitHub Pages (same React→Babel→single-HTML pipeline as
the Ranch Profit Planner, including mandatory compiled-JS content verification
before HTML assembly). Reads data/ files directly. Three views, build order:

1. **Seasonal index view** — rolling 3–5yr weekly price indexes by cls +
   wt_break, per market and blended; overlay current week.
2. **Relationship matrix** — current $/lb and $/hd spreads across weight
   breaks and classes (steer/heifer rollback, feeder→fat, kids→nannies), each
   vs its own historical norm → over/undervalued detection.
3. **VOG panel** — Δ$/hd ÷ Δwt per adjacent weight span per market, compared
   to user BPCOG; feed-vs-buy-weight signal.

Design constraints from the sell-buy framework (docs/sell-buy-reference.md is
the authoritative spec — esp. §8 outputs):
- tier=tradeable barns drive trade views; tier=context summaries drive indexes
- basis handling matters (sheep/goats and bred stock)
- no forecasting features; relationships and current-vs-seasonal-position only
- future Phase 3 rule: sells are never recommended without a paired buy-back

**Needed from Noah at Phase 2 start**: working BPCOG (or COG) per enterprise —
cattle, sheep, goats. Rough is fine; app treats them as editable inputs. If
unavailable, derive from Ranch Profit Planner enterprise data as the opening
exercise.

## Later phases

- **Phase 3**: Notion inventory DB (head counts + weights) synced in; rules
  engine per reference doc §8 — barn cards (EMV), cattle squares, leapfrog
  flags, Female Value Deviation, money-and-grass/capacity constraint checks.
- **Phase 4**: Claude API report layer combining market relationships,
  inventory, feed, cash; narratives as context. Dovetails with the open
  "AI weekly reports" Rock architecture decision (dashboard "Generate Report"
  button was the leading option).
