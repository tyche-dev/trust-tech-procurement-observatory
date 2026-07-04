#!/usr/bin/env python3
"""Deterministic analysis over the frozen consolidated dataset.

Computes EVERY number a findings narrative may cite — so prose can be adversarially
verified against this file (no LLM invents a figure). No network, no deps. Outputs
data/consolidated/analysis.json.
"""
import collections, datetime, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGION = {"USAspending": "US", "FPDS": "US", "UK-ContractsFinder": "UK", "UK-FTS": "UK",
          "TED": "EU", "WorldBank": "Global", "IE-CKAN": "IE"}


def main():
    ds = json.loads((ROOT / "data/consolidated/dataset.json").read_text())
    rels = ds.get("releases", [])
    n = len(rels)

    by_domain = collections.Counter()
    by_region = collections.Counter()
    by_rd = collections.Counter()
    by_country = collections.Counter()
    by_year = collections.Counter()
    by_source = collections.Counter()
    buyers = collections.defaultdict(collections.Counter)   # domain -> buyer counter
    us_value = collections.Counter()                        # domain -> USD sum (US only, has amounts)

    for r in rels:
        src = r.get("tt:source", "?"); rg = REGION.get(src, src)
        by_region[rg] += 1; by_source[src] += 1
        c = (r.get("buyer") or {}).get("country", "")
        if c:
            by_country[c] += 1
        yr = str(r.get("date", ""))[:4]
        if yr.isdigit():
            by_year[yr] += 1
        doms = r.get("tt:domain", [])
        for d in doms:
            by_domain[d] += 1; by_rd[f"{rg}|{d}"] += 1
            bn = (r.get("buyer") or {}).get("name", "")
            if bn:
                buyers[d][bn] += 1
            if src == "USAspending":
                try:
                    amt = float((r.get("awards") or [{}])[0].get("value", {}).get("amount") or 0)
                    us_value[d] += amt
                except Exception:
                    pass

    # PQC gap metric: PQC as share of trust-tech procurement, per region + overall
    def share(dom, rg=None):
        num = by_rd[f"{rg}|{dom}"] if rg else by_domain[dom]
        den = sum(by_rd[f"{rg}|{d}"] for d in ("AI", "PKI", "PQC", "eIDAS")) if rg else sum(by_domain.values())
        return {"count": num, "total": den, "pct": round(100 * num / den, 2) if den else 0.0}

    analysis = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "unique_records": n,
        "by_domain": dict(by_domain),
        "by_region": dict(by_region),
        "by_region_domain": dict(sorted(by_rd.items())),
        "countries_covered": len(by_country),
        "top_countries": dict(by_country.most_common(30)),
        "by_year": dict(sorted(by_year.items())),
        "by_source": dict(by_source),
        "pqc_gap": {
            "overall": share("PQC"),
            "US": share("PQC", "US"), "EU": share("PQC", "EU"), "Global": share("PQC", "Global"),
            "note": "NIST finalized ML-KEM/ML-DSA/SLH-DSA (FIPS 203/204/205) in Aug 2024; NSA CNSA 2.0 sets 2030-2033 migration deadlines. Compare that mandate to the observed PQC procurement share.",
        },
        "ai_vs_security": {
            "ai": by_domain["AI"],
            "security_pki_pqc_eidas": by_domain["PKI"] + by_domain["PQC"] + by_domain["eIDAS"],
        },
        "top_buyers": {d: dict(buyers[d].most_common(10)) for d in ("AI", "PKI", "PQC", "eIDAS")},
        "us_value_usd": {d: round(v) for d, v in us_value.items()},
    }
    (ROOT / "data/consolidated/analysis.json").write_text(json.dumps(analysis, indent=1, ensure_ascii=False))
    print(f"analysis: {n} records | PQC overall {analysis['pqc_gap']['overall']['pct']}% "
          f"| AI {by_domain['AI']} vs security {analysis['ai_vs_security']['security_pki_pqc_eidas']}")
    print("PQC by region:", {k: analysis['pqc_gap'][k] for k in ('US', 'EU', 'Global')})


if __name__ == "__main__":
    main()
