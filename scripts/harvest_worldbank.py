#!/usr/bin/env python3
"""Global harvest: World Bank procurement notices — many borrower countries worldwide.

Covers procurement across dozens of countries (project_ctry_name) in one feed — the
"rest of world" breadth source. Same anti-fabrication contract: live-fetch-or-drop,
per-record provenance, no LLM in loop. Domain assigned by keyword over bid_description/notice_text.

Usage: python3 harvest_worldbank.py --domain PKI [--rows 500]
Source: GET https://search.worldbank.org/api/v2/procnotices?format=json  (open data)
"""
import argparse, csv, datetime, hashlib, json, sys, urllib.request, urllib.parse
from pathlib import Path

API = "https://search.worldbank.org/api/v2/procnotices"
ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (X11; Linux x86_64) tyche-research-observatory"
DOMAIN_KW = {
    "AI": ["artificial intelligence", "machine learning", "automated decision", "algorithm", "deep learning"],
    "PQC": ["post-quantum", "post quantum", "quantum-safe", "quantum resistant", "crypto-agility"],
    "PKI": ["public key infrastructure", "hardware security module", "certificate authority",
            "key management", "code signing", "x.509", " pki ", " hsm "],
    "eIDAS": ["digital identity", "digital wallet", "trust service", "electronic signature",
              "identity verification", "e-signature", "eid "],
}


def get(q, rows, os_):
    url = f"{API}?{urllib.parse.urlencode({'format':'json','rows':rows,'os':os_,'qterm':q})}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.status, r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True, choices=list(DOMAIN_KW))
    ap.add_argument("--rows", type=int, default=200)
    a = ap.parse_args()
    now = datetime.datetime.now(datetime.timezone.utc); today = now.date()
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    run_dir = ROOT / "data" / "raw" / f"worldbank-{a.domain}-{stamp}"; run_dir.mkdir(parents=True, exist_ok=True)
    kws = DOMAIN_KW[a.domain]; out, dropped = [], 0
    for qi, q in enumerate(kws):
        try:
            status, raw = get(q, a.rows, 0)
        except Exception as e:
            print(f"[DROP] {q}: {e}", file=sys.stderr); continue
        if status != 200:
            print(f"[DROP] {q}: HTTP {status}", file=sys.stderr); continue
        (run_dir / f"q{qi}.json").write_bytes(raw)
        for n in json.loads(raw).get("procnotices", []):
            text = ((n.get("bid_description") or "") + " " + (n.get("notice_text") or "")).lower()
            if not any(k.strip() in text for k in kws):
                continue                       # matched broad q but confirm a domain term is present
            nd = str(n.get("noticedate") or "")[:10]
            if nd and nd > today.isoformat():
                dropped += 1; continue
            rec_raw = json.dumps(n, sort_keys=True).encode()
            rh = hashlib.sha256(rec_raw).hexdigest()
            out.append({
                "ocid": f"ttpr-wb-{n.get('id') or rh[:10]}",
                "id": rh[:16], "date": nd, "tag": ["tender"],
                "buyer": {"name": n.get("contact_organization") or n.get("project_name") or "",
                          "country": n.get("project_ctry_name") or n.get("contact_ctry_name") or ""},
                "tender": {"title": (n.get("bid_description") or n.get("project_name") or "")[:300],
                           "classification": {"scheme": "WB-procurement_group",
                                              "id": str(n.get("procurement_group") or ""), "description": ""}},
                "tt:domain": [a.domain], "tt:domain_evidence": f"keyword:{a.domain}",
                "tt:domain_match": "WB-fulltext", "tt:source": "WorldBank",
                "tt:source_url": API, "tt:fetched_at": now.isoformat(), "tt:http_status": 200,
                "tt:raw_hash": rh, "tt:licence": "WorldBank-open"})
    seen, uniq = set(), []
    for r in out:
        if r["ocid"] in seen:
            continue
        seen.add(r["ocid"]); uniq.append(r)
    pkg = {"version": "1.1", "publishedDate": now.isoformat(),
           "publisher": {"name": "Tyche Institute Trust-Tech Procurement Observatory"},
           "license": "https://www.worldbank.org/en/about/legal/terms-and-conditions", "releases": uniq}
    (ROOT / "data" / "releases" / f"worldbank-{a.domain}-{stamp}.json").write_text(json.dumps(pkg, indent=1, ensure_ascii=False))
    man = ROOT / "data" / "releases" / f"worldbank-{a.domain}-{stamp}.manifest.csv"
    with man.open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["ocid", "country", "title", "date", "raw_hash", "fetched_at"])
        for r in uniq:
            w.writerow([r["ocid"], r["buyer"].get("country", ""), r["tender"]["title"][:120],
                        r["date"], r["tt:raw_hash"], r["tt:fetched_at"]])
    print(f"WorldBank domain={a.domain} kept={len(uniq)} future_dropped={dropped} raw={run_dir.name}")


if __name__ == "__main__":
    main()
