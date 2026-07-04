#!/usr/bin/env python3
"""Precision audit of the PQC domain tag.

A record is PQC-CONFIRMED if a genuine post-quantum term appears in its stored title or in
the raw upstream payload it was derived from (joined by publication number for TED, by award
id for USAspending). This is a conservative recount: records that matched a source full-text
index but cannot be confirmed from retrievable text are reported separately as PQC-CANDIDATE.
Writes data/consolidated/pqc-audit.json. No network.
"""
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TERMS = [
    "post-quantum", "post quantum", "postquantum", "quantum-safe", "quantum safe",
    "quantum resistant", "quantum-resistant", "quantensicher", "quantensichere",
    "ml-kem", "ml-dsa", "slh-dsa", "crystals-kyber", "kyber", "dilithium",
    "crypto-agility", "crypto agility", "fips 203", "fips 204", "fips 205",
    "pqc", "quantum cryptograph", "quantum key distribution", "qkd",
    "quantum comput", "quantum threat", "quantum-vulnerable",
]
RE = re.compile("|".join(re.escape(t) for t in TERMS), re.I)


def flatten(x, out):
    if isinstance(x, dict):
        for v in x.values():
            flatten(v, out)
    elif isinstance(x, list):
        for v in x:
            flatten(v, out)
    elif x is not None:
        out.append(str(x))


def raw_text_index():
    """publication-number/award-id -> concatenated raw text, from frozen raw payloads."""
    idx = {}
    for f in glob.glob(str(ROOT / "data/raw/ted-PQC-*/*.json")):
        try:
            doc = json.loads(Path(f).read_text())
        except Exception:
            continue
        for n in doc.get("notices", []):
            key = n.get("publication-number")
            if not key:
                continue
            out = []
            flatten(n, out)
            idx[f"ted:{key}"] = " ".join(out)
    for f in glob.glob(str(ROOT / "data/raw/usaspending-PQC-*/*.json")):
        try:
            doc = json.loads(Path(f).read_text())
        except Exception:
            continue
        for aw in doc.get("results", []):
            key = aw.get("Award ID")
            if not key:
                continue
            out = []
            flatten(aw, out)
            idx[f"usa:{key}"] = " ".join(out)
    return idx


def main():
    ds = json.loads((ROOT / "data/consolidated/dataset.json").read_text())
    idx = raw_text_index()
    confirmed = {"EU": 0, "US": 0}
    candidate = {"EU": 0, "US": 0}
    conf_titles = []
    for r in ds.get("releases", []):
        if "PQC" not in r.get("tt:domain", []):
            continue
        src = r.get("tt:source")
        region = "EU" if src == "TED" else ("US" if src == "USAspending" else "other")
        title = (r.get("tender") or {}).get("title", "")
        ocid = r.get("ocid", "")
        key = None
        if src == "TED":
            key = "ted:" + ocid.replace("ttpr-ted-", "")
        elif src == "USAspending":
            key = "usa:" + ocid.replace("ttpr-usa-", "")
        raw = idx.get(key, "")
        text = title + " " + raw
        if RE.search(text):
            confirmed[region] = confirmed.get(region, 0) + 1
            if len(conf_titles) < 40:
                conf_titles.append({"region": region, "title": title[:90]})
        else:
            candidate[region] = candidate.get(region, 0) + 1

    total_conf = sum(confirmed.values())
    total_cand = sum(candidate.values())
    out = {
        "pqc_matched_total": total_conf + total_cand,
        "pqc_confirmed_total": total_conf,
        "pqc_candidate_only_total": total_cand,
        "confirmed_by_region": confirmed,
        "candidate_only_by_region": candidate,
        "method": "PQC-confirmed = a post-quantum term appears in the stored title or the raw "
                  "upstream payload; PQC-candidate = matched a source full-text/keyword index but "
                  "the retrievable text does not contain a confirming term.",
        "confirmed_titles_sample": conf_titles,
    }
    (ROOT / "data/consolidated/pqc-audit.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"PQC matched={out['pqc_matched_total']} confirmed={total_conf} "
          f"(EU {confirmed.get('EU',0)}, US {confirmed.get('US',0)}) candidate-only={total_cand}")


if __name__ == "__main__":
    main()
