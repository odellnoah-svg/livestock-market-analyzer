# Livestock Market Analyzer

Market report analysis for cattle, sheep, and goat enterprises using sell-buy
marketing principles. Part of the Eubanks Family OS ecosystem.

## Architecture

```
USDA MARS API ──▶ GitHub Actions (weekly / manual) ──▶ data/*.json ──▶ static analyzer app (GitHub Pages)
                                                            ▲
Ranch inventory (Notion) ───────── sync ────────────────────┘
```

- **markets.json** — report slug configuration (21 reports: OK/MO/AR/KS barns +
  regional summaries). `tier: tradeable` barns drive trade recommendations;
  `tier: context` summaries drive seasonal indexes. Paired feeder +
  slaughter/replacement reports share a `market_group`.
- **scripts/fetch_markets.py** — fetch + normalize. Modes: `discover`
  (raw samples for schema review), `backfill --years 5`, `update --days 14`,
  and `renormalize` (rebuilds all of data/ from raw_cache/ with zero API
  calls — use after any normalizer field-mapping change).
- **raw_cache/** — gzipped raw API responses saved during backfill, so
  normalizer fixes never require re-fetching history from USDA.
- **data/{market_group}/{slug_id}_{year}.json** — normalized records,
  per-slug-per-year to keep files small for static hosting. `data/index.json`
  is the manifest.
- **docs/sell-buy-reference.md** — the distilled sell-buy framework
  (formulas + decision rules) that specifies the analysis engine.

## Normalized record schema

| field | meaning |
|---|---|
| date | report date |
| slug_id / market_group / species / tier | from markets.json |
| category | e.g. Feeder Cattle, Slaughter Cattle, Replacement |
| cls | class (Steers, Heifers, Bucks, Does, Wethers...) |
| grade / muscle | frame / quality / muscle grade |
| wt_min / wt_max / wt_avg | weight range, lbs |
| price_min / price_max / price_avg | price range |
| basis | per_cwt or per_head (critical for sheep/goats) |
| head | head count |

## Setup (one-time)

1. Repo secret **MARS_API_KEY** = your MyMarketNews API key
   (Settings → Secrets and variables → Actions).
2. GitHub Pages: Settings → Pages → deploy from branch `main`, root.
3. Run the workflow manually with mode **discover** (Actions → Sync market
   data → Run workflow). Review `samples/` output — especially
   `samples/_unmapped_fields.json` — and adjust the normalizer field map
   if needed.
4. Run mode **backfill** (years = 5). This is a long run; it commits
   `data/` when complete.
5. Weekly `update` runs happen automatically every Friday.

## Phases

- [x] **Phase 1** — data pipeline (this)
- [ ] **Phase 2** — analyzer app: seasonal indexes (3–5 yr rolling),
      price relationship matrix vs historical norms, VOG panel
- [ ] **Phase 3** — inventory integration (Notion) + rules-based
      recommendation engine (barn cards, cattle squares, female value
      deviation, constraint checks)
- [ ] **Phase 4** — AI report layer (Claude API): whole-business briefings
      combining market relationships, inventory, feed, and cash position
