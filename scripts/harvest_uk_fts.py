#!/usr/bin/env python3
"""UK Find a Tender Service (FTS) — above-threshold UK notices, native OCDS 1.1.

Second UK source (complements Contracts Finder's mostly below-threshold notices). No CPV
query param, so we date-window harvest and filter client-side by keyword over title+description,
tagging one or more of the four trust-tech domains. Same anti-fabrication contract:
live-fetch-or-drop, per-record provenance, no LLM in loop.

Usage: python3 harvest_uk_fts.py [--months 18] [--pages-per-window 3]
Source: GET .../api/1.0/ocdsReleasePackages?updatedFrom=&updatedTo=  (OGL v3.0)
"""
import argparse, csv, datetime, hashlib, json, sys, time, urllib.request, urllib.parse
from pathlib import Path

BASE = "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages"
ROOT = Path(__file__).resolve().parent.parent
DOMAIN_KW = {
    "AI": ["artificial intelligence", "machine learning", "automated decision", "algorithm",
           "facial recognition", "large language model", "predictive analytics"],
    "PQC": ["post-quantum", "post quantum", "quantum-safe", "quantum resistant", "crypto-agility", "cnsa"],
    "PKI": ["public key infrastructure", " pki ", "certificate authority", "hardware security module",
            " hsm ", "key management", "code signing", "x.509", "certificate lifecycle"],
    "eIDAS": ["digital identity", "digital wallet", "eidas", "qualified trust service", "qtsp",
              "electronic signature", "identity verification", "electronic identification", "trust service"],
}


def tag(text):
    t = " " + (text or "").lower() + " "
    return [d for d, kws in DOMAIN_KW.items() if any(k in t for k in kws)]


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "tyche-observatory/0.1"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.status, r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=18)
    ap.add_argument("--pages-per-window", type=int, default=3)
    a = ap.parse_args()
    now = datetime.datetime.now(datetime.timezone.utc); today = now.date()
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    run_dir = ROOT / "data" / "raw" / f"uk-fts-{stamp}"; run_dir.mkdir(parents=True, exist_ok=True)
    out, dropped = [], 0
    # monthly windows, most recent first
    end = datetime.datetime(now.year, now.month, 1, tzinfo=datetime.timezone.utc)
    for wi in range(a.months):
        start = end
        # step back one month
        py, pm = (start.year, start.month - 1) if start.month > 1 else (start.year - 1, 12)
        prev = datetime.datetime(py, pm, 1, tzinfo=datetime.timezone.utc)
        q = urllib.parse.urlencode({"updatedFrom": prev.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                    "updatedTo": start.strftime("%Y-%m-%dT%H:%M:%SZ"), "limit": 100})
        url = f"{BASE}?{q}"
        for page in range(a.pages_per_window):
            if not url:
                break
            try:
                status, raw = get(url)
            except Exception as e:
                print(f"[DROP] window {prev.date()} p{page}: {e}", file=sys.stderr); break
            if status != 200:
                print(f"[DROP] window {prev.date()} p{page}: HTTP {status}", file=sys.stderr); break
            (run_dir / f"{prev.strftime('%Y%m')}-{page}.json").write_bytes(raw)
            try:
                doc = json.loads(raw); rels = doc.get("releases", [])
            except Exception:
                break
            url = (doc.get("links") or {}).get("next")
            for rel in rels:
                t = rel.get("tender", {}) or {}
                domains = tag(t.get("title", "") + " " + t.get("description", ""))
                if not domains:
                    continue
                d = str(rel.get("date", ""))[:10]
                if d and d > today.isoformat():
                    dropped += 1; continue
                rec_raw = json.dumps(rel, sort_keys=True).encode()
                rh = hashlib.sha256(rec_raw).hexdigest()
                rel["tt:domain"] = domains
                rel["tt:domain_evidence"] = "keyword:" + ",".join(domains)
                rel["tt:domain_match"] = "FTS-keyword"
                rel["tt:source"] = "UK-FTS"
                rel["tt:source_url"] = BASE
                rel["tt:fetched_at"] = now.isoformat()
                rel["tt:http_status"] = 200
                rel["tt:raw_hash"] = rh
                rel["tt:licence"] = "OGL-v3.0"
                out.append(rel)
            time.sleep(0.4)
        end = prev
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
    (ROOT / "data" / "releases" / f"uk-fts-{stamp}.json").write_text(json.dumps(pkg, indent=1, ensure_ascii=False))
    man = ROOT / "data" / "releases" / f"uk-fts-{stamp}.manifest.csv"
    with man.open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["ocid", "domains", "title", "date", "raw_hash", "fetched_at"])
        for r in uniq:
            w.writerow([r.get("ocid", ""), "|".join(r["tt:domain"]),
                        (r.get("tender", {}) or {}).get("title", "")[:120],
                        r.get("date", "")[:10], r["tt:raw_hash"], r["tt:fetched_at"]])
    print(f"UK-FTS kept={len(uniq)} future_dropped={dropped} raw={run_dir.name}")


if __name__ == "__main__":
    main()
