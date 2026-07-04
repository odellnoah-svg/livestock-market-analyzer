#!/usr/bin/env python3
"""
Livestock Market Analyzer — MARS API fetch & normalize.

Modes:
  discover              Fetch the most recent report per slug, save raw JSON to samples/.
                        Run this FIRST; inspect samples before trusting normalization.
  backfill --years N    Fetch N years of history per slug (default 5), normalize,
                        write data/{market_group}/{slug_id}_{year}.json
  update  --days N      Fetch the last N days (default 14), merge into current-year files.

Auth: MARS_API_KEY env var (HTTP basic auth, key as username, blank password).
Data layout is per-slug-per-year to keep individual files small for static hosting.
"""

import argparse
import gzip
import json
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import base64

BASE = "https://marsapi.ams.usda.gov/services/v1.2/reports"
ROOT = Path(__file__).resolve().parent.parent
RATE_LIMIT_SLEEP = 1.5   # seconds between requests — be polite to USDA
MAX_RETRIES = 3

# ---------------------------------------------------------------- http

def api_get(path_and_query: str, api_key: str):
    url = f"{BASE}/{path_and_query}"
    auth = base64.b64encode(f"{api_key}:".encode()).decode()
    req = Request(url, headers={"Authorization": f"Basic {auth}",
                                "Accept": "application/json"})
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            if e.code == 404:
                return None  # no data for this slug/range
            if e.code in (429, 500, 502, 503) and attempt < MAX_RETRIES:
                wait = 10 * attempt
                print(f"    HTTP {e.code}, retry {attempt}/{MAX_RETRIES} in {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise
        except URLError as e:
            if attempt < MAX_RETRIES:
                time.sleep(10 * attempt)
                continue
            raise
    return None


def extract_rows(payload):
    """MARS responses are either a bare list of rows or {'results': [...]}."""
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return payload.get("results", payload.get("Results", []))
    return []

# ---------------------------------------------------------------- normalize

def first(row, *keys):
    """Return the first present, non-empty value among candidate field names."""
    for k in keys:
        if k in row and row[k] not in (None, "", "null"):
            return row[k]
    return None


def to_float(v):
    if v is None:
        return None
    try:
        return float(str(v).replace(",", "").replace("$", ""))
    except ValueError:
        return None


def to_int(v):
    f = to_float(v)
    return int(f) if f is not None else None


def normalize_row(row, meta):
    """Map a raw MARS row to the analyzer schema. Unknown-field names are
    collected by the caller for schema review after the first real run."""
    price_basis = first(row, "price_unit", "unit", "pricing_basis") or ""
    price_basis = str(price_basis).lower()
    if "head" in price_basis:
        basis = "per_head"
    elif "cwt" in price_basis or "hundred" in price_basis:
        basis = "per_cwt"
    else:
        basis = price_basis or None  # keep raw; resolve after discovery

    return {
        "date": first(row, "report_date", "report_begin_date", "published_date"),
        "slug_id": meta["slug_id"],
        "market_group": meta["market_group"],
        "species": meta["species"],
        "tier": meta["tier"],
        "category": first(row, "category", "commodity_category"),
        "commodity": first(row, "commodity"),
        "cls": first(row, "class", "class_name"),
        "grade": first(row, "frame", "quality_grade_name", "grade"),
        "muscle": first(row, "muscle_grade"),
        "wt_min": to_float(first(row, "avg_weight_min", "weight_range_low", "low_weight")),
        "wt_max": to_float(first(row, "avg_weight_max", "weight_range_high", "high_weight")),
        "wt_avg": to_float(first(row, "avg_weight", "average_weight")),
        "price_min": to_float(first(row, "avg_price_min", "price_range_low", "low_price")),
        "price_max": to_float(first(row, "avg_price_max", "price_range_high", "high_price")),
        "price_avg": to_float(first(row, "avg_price", "average_price", "wtd_avg_price")),
        "basis": basis,
        "head": to_int(first(row, "head_count", "headcount", "receipts")),
        "lot_desc": first(row, "lot_desc", "comments", "offering"),
    }


KNOWN_FIELDS = {
    "report_date", "report_begin_date", "report_end_date", "published_date",
    "category", "commodity_category", "commodity", "class", "class_name",
    "frame", "quality_grade_name", "grade", "muscle_grade",
    "avg_weight_min", "weight_range_low", "low_weight",
    "avg_weight_max", "weight_range_high", "high_weight",
    "avg_weight", "average_weight",
    "avg_price_min", "price_range_low", "low_price",
    "avg_price_max", "price_range_high", "high_price",
    "avg_price", "average_price", "wtd_avg_price",
    "price_unit", "unit", "pricing_basis",
    "head_count", "headcount", "receipts",
    "lot_desc", "comments", "offering",
}

# ---------------------------------------------------------------- modes

def load_config():
    with open(ROOT / "markets.json") as f:
        return json.load(f)["reports"]


def mode_discover(api_key):
    outdir = ROOT / "samples"
    outdir.mkdir(exist_ok=True)
    unseen_fields = {}
    today = date.today()
    start = today - timedelta(days=10)
    q = f"report_begin_date={start.strftime('%m/%d/%Y')}:{today.strftime('%m/%d/%Y')}"
    for meta in load_config():
        sid = meta["slug_id"]
        print(f"[{sid}] {meta['title']} ...", flush=True)
        payload = api_get(f"{sid}?q={quote(q, safe='=:/')}", api_key)
        rows = extract_rows(payload)
        sample = rows[:300]  # schema inspection only — keep files small
        with open(outdir / f"{sid}.json", "w") as f:
            json.dump(sample, f, indent=2)
        if rows:
            fields = set().union(*(r.keys() for r in rows if isinstance(r, dict)))
            unknown = sorted(fields - KNOWN_FIELDS)
            if unknown:
                unseen_fields[sid] = unknown
            print(f"    {len(rows)} rows, {len(fields)} fields "
                  f"({len(unknown)} unmapped)", flush=True)
        else:
            print("    NO ROWS — check slug or report availability", flush=True)
        time.sleep(RATE_LIMIT_SLEEP)
    with open(outdir / "_unmapped_fields.json", "w") as f:
        json.dump(unseen_fields, f, indent=2)
    print("\nDiscovery complete. Review samples/ and samples/_unmapped_fields.json "
          "before running backfill.")


def fetch_range(meta, start: date, end: date, api_key, cache_year=None):
    """Fetch a slug over a date range using MARS q= range syntax, normalize rows.
    If cache_year is given, the raw payload is gzipped into raw_cache/ so the
    normalizer can be iterated later without re-hitting the API."""
    q = f"report_begin_date={start.strftime('%m/%d/%Y')}:{end.strftime('%m/%d/%Y')}"
    payload = api_get(f"{meta['slug_id']}?q={quote(q, safe='=:/')}", api_key)
    if cache_year is not None and payload is not None:
        cdir = ROOT / "raw_cache" / meta["market_group"]
        cdir.mkdir(parents=True, exist_ok=True)
        with gzip.open(cdir / f"{meta['slug_id']}_{cache_year}.json.gz", "wt") as f:
            json.dump(payload, f)
    rows = extract_rows(payload)
    return [normalize_row(r, meta) for r in rows if isinstance(r, dict)]


def write_year_file(meta, year, records):
    d = ROOT / "data" / meta["market_group"]
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{meta['slug_id']}_{year}.json"
    records.sort(key=lambda r: (r["date"] or "", r["cls"] or "", r["wt_avg"] or 0))
    with open(path, "w") as f:
        json.dump(records, f, separators=(",", ":"))
    return path, len(records)


def mode_backfill(api_key, years):
    today = date.today()
    manifest = []
    for meta in load_config():
        print(f"[{meta['slug_id']}] {meta['title']}", flush=True)
        for y in range(today.year - years, today.year + 1):
            start = date(y, 1, 1)
            end = min(date(y, 12, 31), today)
            if start > today:
                continue
            try:
                recs = fetch_range(meta, start, end, api_key, cache_year=y)
            except Exception as e:
                print(f"    {y}: ERROR {e}", flush=True)
                continue
            if recs:
                path, n = write_year_file(meta, y, recs)
                manifest.append({"slug_id": meta["slug_id"], "year": y,
                                 "records": n, "file": str(path.relative_to(ROOT))})
                print(f"    {y}: {n} records", flush=True)
            else:
                print(f"    {y}: no data", flush=True)
            time.sleep(RATE_LIMIT_SLEEP)
    write_index(manifest)


def mode_update(api_key, days):
    today = date.today()
    start = today - timedelta(days=days)
    for meta in load_config():
        try:
            recs = fetch_range(meta, start, today, api_key)
        except Exception as e:
            print(f"[{meta['slug_id']}] ERROR {e}", flush=True)
            continue
        if not recs:
            print(f"[{meta['slug_id']}] no new data", flush=True)
            time.sleep(RATE_LIMIT_SLEEP)
            continue
        by_year = {}
        for r in recs:
            y = (r["date"] or str(today))[-4:] if "/" in str(r["date"] or "") \
                else str(r["date"] or today.isoformat())[:4]
            by_year.setdefault(y, []).append(r)
        for y, new in by_year.items():
            path = ROOT / "data" / meta["market_group"] / f"{meta['slug_id']}_{y}.json"
            existing = []
            if path.exists():
                with open(path) as f:
                    existing = json.load(f)
            key = lambda r: (r["date"], r["cls"], r["grade"], r["wt_min"],
                             r["wt_max"], r["price_avg"], r["head"])
            seen = {key(r) for r in existing}
            merged = existing + [r for r in new if key(r) not in seen]
            write_year_file(meta, y, merged)
            print(f"[{meta['slug_id']}] {y}: +{len(merged) - len(existing)} "
                  f"(total {len(merged)})", flush=True)
        time.sleep(RATE_LIMIT_SLEEP)
    rebuild_index()



def mode_renormalize():
    """Rebuild all of data/ from raw_cache/ — no API calls. Use after any
    change to the normalizer field mapping."""
    cfg = {m["slug_id"]: m for m in load_config()}
    cache = sorted((ROOT / "raw_cache").glob("*/*.json.gz"))
    if not cache:
        sys.exit("raw_cache/ is empty — run backfill first")
    for p in cache:
        sid, year = p.stem.replace(".json", "").split("_")
        meta = cfg.get(int(sid))
        if meta is None:
            print(f"skip {p} (slug not in markets.json)")
            continue
        with gzip.open(p, "rt") as f:
            payload = json.load(f)
        recs = [normalize_row(r, meta) for r in extract_rows(payload)
                if isinstance(r, dict)]
        _, n = write_year_file(meta, year, recs)
        print(f"[{sid}] {year}: {n} records")
    rebuild_index()


def write_index(manifest):
    with open(ROOT / "data" / "index.json", "w") as f:
        json.dump({"generated": date.today().isoformat(),
                   "files": manifest}, f, indent=2)


def rebuild_index():
    manifest = []
    dataroot = ROOT / "data"
    for p in sorted(dataroot.glob("*/*.json")):
        sid, year = p.stem.split("_")
        with open(p) as f:
            n = len(json.load(f))
        manifest.append({"slug_id": int(sid), "year": int(year),
                         "records": n, "file": str(p.relative_to(ROOT))})
    write_index(manifest)


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["discover", "backfill", "update", "renormalize"])
    ap.add_argument("--years", type=int, default=5)
    ap.add_argument("--days", type=int, default=14)
    args = ap.parse_args()

    if args.mode == "renormalize":
        mode_renormalize()
        return

    api_key = os.environ.get("MARS_API_KEY")
    if not api_key:
        sys.exit("MARS_API_KEY environment variable not set")

    if args.mode == "discover":
        mode_discover(api_key)
    elif args.mode == "backfill":
        mode_backfill(api_key, args.years)
    else:
        mode_update(api_key, args.days)


if __name__ == "__main__":
    main()
