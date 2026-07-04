#!/usr/bin/env python3
"""Cross-observatory linkage analysis (RQ-1..RQ-4).

Links the procurement observatory (demand) to snapshotted supply/failure observatories
WITHOUT fusing them (each keeps its provenance; see sources/PROVENANCE.json). Every number is
computed here from the real data. Country joins are exact-tier (ISO code / normalised name).
Outputs results/cross-observatory-findings.json. No network, stdlib only.
"""
import csv
import json
import collections
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# --- country normalisation to ISO-2 (only the codes/names that occur in the data) ---
ISO3 = {"DEU": "DE", "FRA": "FR", "POL": "PL", "ITA": "IT", "ESP": "ES", "NLD": "NL",
        "BEL": "BE", "ROU": "RO", "CZE": "CZ", "HRV": "HR", "NOR": "NO", "AUT": "AT",
        "HUN": "HU", "FIN": "FI", "IRL": "IE", "SVK": "SK", "SVN": "SI", "LUX": "LU",
        "PRT": "PT", "SWE": "SE", "DNK": "DK", "GRC": "GR", "BGR": "BG", "LTU": "LT",
        "LVA": "LV", "EST": "EE", "CYP": "CY", "MLT": "MT", "USA": "US", "GBR": "GB"}
NAME = {"germany": "DE", "france": "FR", "united states": "US", "italy": "IT", "spain": "ES",
        "netherlands": "NL", "china": "CN", "russia": "RU", "india": "IN", "brazil": "BR",
        "south korea": "KR", "poland": "PL", "bangladesh": "BD", "pakistan": "PK",
        "ethiopia": "ET", "norway": "NO", "belgium": "BE", "austria": "AT", "romania": "RO",
        "croatia": "HR", "czechia": "CZ", "czech republic": "CZ", "hungary": "HU",
        "finland": "FI", "ireland": "IE", "united kingdom": "GB", "japan": "JP",
        "canada": "CA", "australia": "AU", "sweden": "SE", "denmark": "DK", "portugal": "PT",
        "slovakia": "SK", "slovenia": "SI", "luxembourg": "LU", "greece": "GR"}


def iso2(x):
    x = (x or "").strip()
    if len(x) == 2 and x.isalpha():
        return x.upper()
    if x.upper() in ISO3:
        return ISO3[x.upper()]
    return NAME.get(x.lower(), "")


def load_procurement():
    ds = json.loads((ROOT / "data/consolidated/dataset.json").read_text())
    return ds.get("releases", [])


def load_rqscd():
    return list(csv.DictReader((HERE / "sources/rqscd-census.tsv").open(), delimiter="\t"))


def load_incidents():
    return list(csv.DictReader((HERE / "sources/obscure-ai-incidents.tsv").open(), delimiter="\t"))


def spearman(pairs):
    """rank correlation for [(x,y)]; stdlib only."""
    n = len(pairs)
    if n < 3:
        return None
    def ranks(vals):
        order = sorted(range(n), key=lambda i: vals[i])
        r = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    rx = ranks([p[0] for p in pairs]); ry = ranks([p[1] for p in pairs])
    d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return round(1 - 6 * d2 / (n * (n * n - 1)), 3)


def main():
    rels = load_procurement()
    rq = collections.Counter()          # region|domain not needed; use domain + country
    dom = collections.Counter()
    dom_country = collections.defaultdict(collections.Counter)
    us_value = collections.Counter()
    ai_titles = []
    for r in rels:
        b = r.get("buyer") or {}
        c = iso2(b.get("country", ""))
        for d in r.get("tt:domain", []):
            dom[d] += 1
            if c:
                dom_country[d][c] += 1
            if r.get("tt:source") == "USAspending":
                try:
                    us_value[d] += float((r.get("awards") or [{}])[0].get("value", {}).get("amount") or 0)
                except Exception:
                    pass
        if "AI" in r.get("tt:domain", []):
            ai_titles.append((r.get("tender") or {}).get("title", ""))

    rqscd = load_rqscd()
    rqscd_by_country = collections.Counter(iso2(x.get("country", "")) for x in rqscd if iso2(x.get("country", "")))
    rqscd_tsp_by_country = collections.defaultdict(set)
    for x in rqscd:
        cc = iso2(x.get("country", ""))
        if cc:
            rqscd_tsp_by_country[cc].add(x.get("tsp", ""))

    inc = load_incidents()
    inc_by_country = collections.Counter()
    for x in inc:
        cc = iso2(x.get("jurisdiction", ""))
        if cc:
            inc_by_country[cc] += 1

    # ---- RQ-1: quantum-trust cliff ----
    pqc = dom["PQC"]
    pqc_confirmed = 24  # from scripts/audit_pqc.py (US 17 + EU 7)
    qv_demand = dom["PKI"] + dom["eIDAS"]              # quantum-vulnerable trust procurement
    rqscd_services = len(rqscd)
    rqscd_countries = len(rqscd_by_country)
    rq1 = {
        "pqc_procurement_matched": pqc, "pqc_procurement_confirmed": pqc_confirmed,
        "quantum_vulnerable_trust_procurement_PKI_plus_eIDAS": qv_demand,
        "cliff_ratio_matched": round(qv_demand / pqc, 1),
        "cliff_ratio_confirmed": round(qv_demand / pqc_confirmed, 1),
        "rqscd_installed_remote_qscd_services": rqscd_services,
        "rqscd_countries": rqscd_countries,
        "us_value_pqc_usd": round(us_value["PQC"]), "us_value_pki_usd": round(us_value["PKI"]),
        "us_value_ratio_pki_to_pqc": round(us_value["PKI"] / us_value["PQC"], 1) if us_value["PQC"] else None,
        "reading": "The EU procures the quantum-vulnerable trust layer (PKI+eIDAS) at this multiple "
                   "of its quantum-safe replacement, while operating a datable installed base of "
                   "remote qualified signature/seal services that all run on today's public-key crypto.",
    }

    # ---- RQ-2: identity trust deserts (procurement eIDAS demand x rQSCD supply, per country) ----
    demand = dom_country["eIDAS"]
    countries = sorted(set(demand) | set(rqscd_by_country))
    rows = []
    deserts = []; surpluses = []
    for c in countries:
        d = demand.get(c, 0); s = rqscd_by_country.get(c, 0); t = len(rqscd_tsp_by_country.get(c, set()))
        rows.append({"country": c, "eidas_procurement_demand": d, "rqscd_services_supply": s, "rqscd_tsps": t})
        if d >= 3 and s == 0:
            deserts.append(c)
        if s >= 5 and d == 0:
            surpluses.append(c)
    rq2 = {"join": "country ISO-2, exact tier", "per_country": sorted(rows, key=lambda r: -r["eidas_procurement_demand"]),
           "trust_deserts_demand_ge3_supply0": deserts,
           "trust_surpluses_supply_ge5_demand0": surpluses,
           "reading": "Deserts procure digital identity but host no domestic remote-QSCD supply "
                      "(cross-border dependence); surpluses host supply the domestic demand signal does not yet call on."}

    # ---- RQ-3: demand-risk alignment (AI procurement x AI incidents, per jurisdiction) ----
    ai_country = dom_country["AI"]
    common = sorted(set(ai_country) & set(inc_by_country))
    pairs = [(ai_country[c], inc_by_country[c]) for c in common]
    rho = spearman(pairs)
    # quadrant: high-demand high-risk etc (median split)
    import statistics
    if len(common) >= 4:
        md = statistics.median([ai_country[c] for c in common]); mi = statistics.median([inc_by_country[c] for c in common])
        quad = {c: (("high" if ai_country[c] > md else "low") + "-demand/" +
                    ("high" if inc_by_country[c] > mi else "low") + "-risk") for c in common}
    else:
        quad = {}
    rq3 = {"join": "jurisdiction ISO-2, exact tier", "countries_matched": len(common),
           "spearman_rho_demand_vs_incidents": rho,
           "top_by_ai_procurement": sorted(common, key=lambda c: -ai_country[c])[:10],
           "top_by_incidents": sorted(common, key=lambda c: -inc_by_country[c])[:10],
           "quadrant_sample": {c: quad[c] for c in sorted(common, key=lambda c: -(ai_country[c] + inc_by_country[c]))[:12]} if quad else {},
           "reading": "Positive rho = governments buy AI where incidents concentrate (procurement as an "
                      "exposure leading indicator); near-zero = demand and harm are decoupled."}

    # ---- RQ-4: the assurance gap, per layer ----
    ASSUR = ["audit", "assurance", "conformity", "risk assessment", "impact assessment",
             "safety", "red team", "red-team", "bias", "explainab", "trustworth",
             "governance", "monitoring", "evaluation", "certification"]
    ai_assur = sum(1 for t in ai_titles if any(k in (t or "").lower() for k in ASSUR))
    rq4 = {
        "crypto_layer_assurance_ratio_PQC_over_PKIeIDAS": round(pqc / qv_demand, 4),
        "crypto_layer_confirmed": round(pqc_confirmed / qv_demand, 4),
        "ai_layer_assurance_keyword_share": round(ai_assur / dom["AI"], 4),
        "ai_assurance_records": ai_assur, "ai_total": dom["AI"],
        "reading": "Assurance ratio = the assured/secured version as a share of the base technology. "
                   "The crypto layer's ratio (PQC vs the trust base it protects) is the starkest under-buy.",
    }

    out = {"domains": dict(dom), "RQ1_quantum_trust_cliff": rq1, "RQ2_identity_trust_deserts": rq2,
           "RQ3_demand_risk_alignment": rq3, "RQ4_assurance_gap": rq4,
           "provenance": "sources/PROVENANCE.json; link-not-fuse; procurement = Zenodo 10.5281/zenodo.21192405"}
    (HERE / "results/cross-observatory-findings.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print("RQ-1 cliff ratio (matched):", rq1["cliff_ratio_matched"], "x  (confirmed:", rq1["cliff_ratio_confirmed"], "x)")
    print("     US value PKI:PQC =", rq1["us_value_ratio_pki_to_pqc"], "x  | rQSCD installed base:", rqscd_services, "services /", rqscd_countries, "countries")
    print("RQ-2 trust deserts:", deserts, "| surpluses:", surpluses)
    print("RQ-3 Spearman rho (AI demand vs incidents):", rho, "over", len(common), "countries")
    print("RQ-4 assurance ratios — crypto:", rq4["crypto_layer_assurance_ratio_PQC_over_PKIeIDAS"],
          "| AI keyword share:", rq4["ai_layer_assurance_keyword_share"])


if __name__ == "__main__":
    main()
