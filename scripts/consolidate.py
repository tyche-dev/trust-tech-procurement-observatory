#!/usr/bin/env python3
"""Consolidate all release packages into a single deduped dataset + honest stats.

Lanes run daily and each harvest writes a new package; the SAME procurement record recurs
across runs. This dedups by ocid (keeping the latest fetch by tt:fetched_at) so counts
reflect UNIQUE procurement records, never harvest-run copies. Writes:
  data/consolidated/dataset.json   — one OCDS package, unique releases
  data/consolidated/stats.json     — unique counts by region x domain, country list
No network, no deps. Run after any harvest.
"""
import json, glob, collections, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGION = {"USAspending": "US", "FPDS": "US", "UK-ContractsFinder": "UK", "UK-FTS": "UK",
          "TED": "EU", "WorldBank": "Global", "IE-CKAN": "IE"}


def main():
    best = {}
    for f in sorted(glob.glob(str(ROOT / "data/releases/*.json"))):
        try:
            pkg = json.loads(Path(f).read_text())
        except Exception:
            continue
        for r in pkg.get("releases", []):
            oc = r.get("ocid")
            if not oc:
                continue
            prev = best.get(oc)
            if prev is None or str(r.get("tt:fetched_at", "")) >= str(prev.get("tt:fetched_at", "")):
                best[oc] = r
    releases = list(best.values())
    outdir = ROOT / "data" / "consolidated"; outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "dataset.json").write_text(json.dumps(
        {"version": "1.1", "publisher": {"name": "Tyche Trust-Tech Procurement Observatory"},
         "releases": releases}, indent=1, ensure_ascii=False))

    by_rd = collections.Counter(); countries = collections.Counter(); by_src = collections.Counter()
    for r in releases:
        src = r.get("tt:source", "?"); rg = REGION.get(src, src)
        by_src[src] += 1
        c = (r.get("buyer", {}) or {}).get("country", "")
        if c:
            countries[c] += 1
        for d in r.get("tt:domain", []):
            by_rd[f"{rg}|{d}"] += 1
    stats = {"generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "unique_records": len(releases),
             "by_region_domain": dict(sorted(by_rd.items())),
             "by_source": dict(by_src),
             "countries_covered": len(countries),
             "by_country": dict(countries.most_common())}
    (outdir / "stats.json").write_text(json.dumps(stats, indent=1, ensure_ascii=False))
    print(f"consolidated: {len(releases)} unique records, {len(countries)} countries")
    print("by region x domain:", dict(sorted(by_rd.items())))


if __name__ == "__main__":
    main()
