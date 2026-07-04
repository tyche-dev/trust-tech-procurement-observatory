#!/usr/bin/env python3
"""Phase-1 harvest: US federal awards for a trust-tech domain via USAspending.gov.

ANTI-FABRICATION BY CONSTRUCTION. This script is the ONLY way a record enters the
observatory for this source. Every emitted record carries:
  tt:source_url, tt:fetched_at, tt:http_status(==200), tt:raw_hash(sha256 of the raw
  upstream award object). No live 200 -> no record. There is no manual-insert path and
  no LLM in this loop. Counts are whatever is on disk; nobody "estimates".

Usage:  python3 harvest_usaspending.py --domain PQC [--limit 100] [--pages 5]
Source: POST https://api.usaspending.gov/api/v2/search/spending_by_award/  (no auth)
Licence of data: US federal public domain.
"""
import argparse, csv, datetime, hashlib, json, sys, time, urllib.request, urllib.error
from pathlib import Path

API = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
ROOT = Path(__file__).resolve().parent.parent

# Keyword sets are the domain selector for keyword-dominant domains (verified live in
# the blueprint run). Codes/keywords must stay in sync with methods/domain-selection.md.
DOMAIN_KEYWORDS = {
    "PQC": ["post-quantum cryptography", "post quantum cryptography", "quantum-safe",
            "quantum resistant cryptography", "CNSA 2.0", "ML-KEM", "FIPS 203"],
    "PKI": ["public key infrastructure", "hardware security module", "certificate authority",
            "key management system", "code signing certificate", "X.509 certificate"],
    "AI": ["artificial intelligence system", "machine learning model", "automated decision system",
           "large language model", "facial recognition system"],
    "eIDAS": ["digital identity wallet", "qualified trust service", "electronic identity verification",
              "qualified electronic signature"],
}
FIELDS = ["Award ID", "Recipient Name", "Award Amount", "Description",
          "Action Date", "Awarding Agency", "Awarding Sub Agency", "naics_code"]


def post(payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(API, data=data, headers={"Content-Type": "application/json",
                                                          "User-Agent": "tyche-observatory/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True, choices=list(DOMAIN_KEYWORDS))
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--pages", type=int, default=5)
    a = ap.parse_args()

    now = datetime.datetime.now(datetime.timezone.utc)
    today = now.date()
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    run_dir = ROOT / "data" / "raw" / f"usaspending-{a.domain}-{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    releases, dropped = [], 0

    for kw in DOMAIN_KEYWORDS[a.domain]:
        for page in range(1, a.pages + 1):
            payload = {"filters": {"award_type_codes": ["A", "B", "C", "D"], "keywords": [kw]},
                       "fields": FIELDS, "page": page, "limit": a.limit,
                       "order": "desc", "sort": "Award Amount"}
            try:
                status, raw = post(payload)
            except urllib.error.HTTPError as e:
                status, raw = e.code, b""
            except Exception as e:
                print(f"[DROP] {kw} p{page}: {e}", file=sys.stderr); continue
            if status != 200:                      # live-fetch-or-drop
                print(f"[DROP] {kw} p{page}: HTTP {status}", file=sys.stderr); continue
            (run_dir / f"{hashlib.sha1((kw+str(page)).encode()).hexdigest()[:12]}.json").write_bytes(raw)
            results = json.loads(raw).get("results", [])
            if not results:
                break
            for aw in results:
                rec_raw = json.dumps(aw, sort_keys=True).encode()
                raw_hash = hashlib.sha256(rec_raw).hexdigest()
                adate = (aw.get("Action Date") or "")[:10]
                if adate and adate > today.isoformat():   # future-date guard
                    dropped += 1; continue
                releases.append({
                    "ocid": f"ttpr-usa-{aw.get('Award ID') or ('nohash-'+raw_hash[:8])}",
                    "id": raw_hash[:16], "date": adate, "tag": ["award"],
                    "buyer": {"name": aw.get("Awarding Agency") or ""},
                    "tender": {"title": (aw.get("Description") or "")[:300],
                               "classification": {"scheme": "NAICS", "id": str(aw.get("naics_code") or ""),
                                                  "description": ""}},
                    "awards": [{"suppliers": [{"name": aw.get("Recipient Name") or ""}],
                                "value": {"amount": aw.get("Award Amount") or 0, "currency": "USD"},
                                "date": adate}],
                    "tt:domain": [a.domain], "tt:domain_evidence": f"keyword:{kw}",
                    "tt:source": "USAspending", "tt:source_url": API,
                    "tt:fetched_at": now.isoformat(), "tt:http_status": 200,
                    "tt:raw_hash": raw_hash, "tt:licence": "US-Public-Domain"})
            time.sleep(0.5)                          # polite backoff

    # dedupe by ocid (same award can surface under multiple keywords)
    seen, uniq = set(), []
    for r in releases:
        if r["ocid"] in seen:
            continue
        seen.add(r["ocid"]); uniq.append(r)

    pkg = {"version": "1.1", "publishedDate": now.isoformat(),
           "publisher": {"name": "Tyche Institute Trust-Tech Procurement Observatory"},
           "license": "https://standard.open-contracting.org/1.1/en/",
           "releases": uniq}
    rel_path = ROOT / "data" / "releases" / f"usaspending-{a.domain}-{stamp}.json"
    rel_path.write_text(json.dumps(pkg, indent=1))

    man = ROOT / "data" / "releases" / f"usaspending-{a.domain}-{stamp}.manifest.csv"
    with man.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ocid", "recipient", "amount_usd", "action_date", "buyer",
                    "domain_evidence", "raw_hash", "fetched_at"])
        for r in uniq:
            w.writerow([r["ocid"], r["awards"][0]["suppliers"][0]["name"],
                        r["awards"][0]["value"]["amount"], r["date"], r["buyer"]["name"],
                        r["tt:domain_evidence"], r["tt:raw_hash"], r["tt:fetched_at"]])
    print(f"domain={a.domain} kept={len(uniq)} future_dropped={dropped} "
          f"raw={run_dir} releases={rel_path.name}")


if __name__ == "__main__":
    main()
