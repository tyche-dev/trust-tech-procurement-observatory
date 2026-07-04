#!/usr/bin/env python3
"""Phase-3 harvest: UK Contracts Finder — native OCDS 1.1, no transform risk.

Same anti-fabrication contract as harvest_usaspending.py: live-fetch-or-drop, provenance
required (tt:source_url / tt:fetched_at / tt:http_status==200 / tt:raw_hash), no LLM in loop.
Contracts Finder is native OCDS so we keep the upstream release and only ADD tt: fields +
a keyword-based domain tag. CPV codes are the verified allowlist.

Usage: python3 harvest_uk_contractsfinder.py [--pages 3]
Source: GET .../Published/Notices/OCDS/Search?cpv_codes=<code>  (OGL v3.0)
"""
import argparse, csv, datetime, hashlib, json, sys, time, urllib.request, urllib.parse
from pathlib import Path

BASE = "https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search"
ROOT = Path(__file__).resolve().parent.parent
CPV = {"72000000": "IT services", "48000000": "Software packages",
       "79417000": "Security consultancy", "48732000": "Data security software"}
DOMAIN_KW = {
    "AI": ["artificial intelligence", "machine learning", "automated decision", "algorithm", "facial recognition"],
    "PQC": ["post-quantum", "quantum-safe", "quantum resistant", "crypto-agility", "cnsa"],
    "PKI": ["public key infrastructure", " pki ", "certificate authority", "hardware security module",
            "hsm", "key management", "code signing", "x.509", "certificate lifecycle"],
    "eIDAS": ["eidas", "digital identity", "digital wallet", "eudi", "qscd", "qtsp",
              "qualified trust service", "electronic signature", "identity verification"],
}


def tag_domains(text):
    t = (" " + (text or "").lower() + " ")
    return [d for d, kws in DOMAIN_KW.items() if any(k in t for k in kws)]


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "User-Agent": "tyche-observatory/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--pages", type=int, default=2); a = ap.parse_args()
    now = datetime.datetime.now(datetime.timezone.utc); today = now.date()
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    run_dir = ROOT / "data" / "raw" / f"uk-contractsfinder-{stamp}"; run_dir.mkdir(parents=True, exist_ok=True)
    out, dropped = [], 0
    for cpv in CPV:
        q = urllib.parse.urlencode({"cpv_codes": cpv, "limit": 100})
        url = f"{BASE}?{q}"
        for page in range(1, a.pages + 1):
            if not url:
                break
            try:
                status, raw = get(url)
            except Exception as e:
                print(f"[DROP] cpv {cpv} p{page}: {e}", file=sys.stderr); break
            if status != 200:
                print(f"[DROP] cpv {cpv} p{page}: HTTP {status}", file=sys.stderr); break
            (run_dir / f"{cpv}-{page}.json").write_bytes(raw)
            try:
                doc = json.loads(raw); results = doc.get("releases", [])
            except Exception:
                break
            url = (doc.get("links") or {}).get("next")   # OCDS pagination
            if not results:
                break
            for rel in results:
                rec_raw = json.dumps(rel, sort_keys=True).encode()
                raw_hash = hashlib.sha256(rec_raw).hexdigest()
                t = rel.get("tender", {}) or {}
                text = (t.get("title", "") + " " + t.get("description", ""))
                domains = tag_domains(text)
                if not domains:
                    continue                     # cpv net matched but no domain keyword -> not counted
                d = str(rel.get("date", ""))[:10]
                if d and d > today.isoformat():
                    dropped += 1; continue
                rel["tt:domain"] = domains
                rel["tt:domain_evidence"] = f"cpv:{cpv}"
                rel["tt:domain_keyword_gated"] = True
                rel["tt:source"] = "UK-ContractsFinder"
                rel["tt:source_url"] = BASE
                rel["tt:fetched_at"] = now.isoformat()
                rel["tt:http_status"] = 200
                rel["tt:raw_hash"] = raw_hash
                rel["tt:licence"] = "OGL-v3.0"
                out.append(rel)
            time.sleep(0.5)
    seen, uniq = set(), []
    for r in out:
        k = r.get("ocid") or r.get("id") or r["tt:raw_hash"]
        if k in seen:
            continue
        seen.add(k); uniq.append(r)
    pkg = {"version": "1.1", "publishedDate": now.isoformat(),
           "publisher": {"name": "Tyche Institute Trust-Tech Procurement Observatory"},
           "license": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
           "releases": uniq}
    (ROOT / "data" / "releases" / f"uk-contractsfinder-{stamp}.json").write_text(json.dumps(pkg, indent=1))
    man = ROOT / "data" / "releases" / f"uk-contractsfinder-{stamp}.manifest.csv"
    with man.open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["ocid", "title", "domains", "date", "raw_hash", "fetched_at"])
        for r in uniq:
            w.writerow([r.get("ocid", ""), (r.get("tender", {}) or {}).get("title", "")[:120],
                        "|".join(r["tt:domain"]), r.get("date", "")[:10], r["tt:raw_hash"], r["tt:fetched_at"]])
    print(f"UK kept={len(uniq)} future_dropped={dropped} raw={run_dir.name}")


if __name__ == "__main__":
    main()
