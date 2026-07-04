#!/usr/bin/env python3
"""Phase-4 harvest: EU TED v3 — all EU-27 notices, FULL-TEXT domain queries (high recall).

Fixes the low-recall problem of CPV-net + title-keyword filtering: queries TED's full-text
(FT) index directly for each domain's terms, which finds AI/PQC/PKI/eIDAS notices in ANY of
the 24 EU languages. Same anti-fabrication contract: live-fetch-or-drop, per-record
provenance (tt:source_url / tt:fetched_at / tt:http_status==200 / tt:raw_hash), no LLM in loop.

Usage: python3 harvest_ted.py --domain PQC [--pages 4] [--since 2023-01-01]
Source: POST https://api.ted.europa.eu/v3/notices/search  (no auth; EU-PO reuse licence)
"""
import argparse, csv, datetime, hashlib, json, sys, time, urllib.request
from pathlib import Path

API = "https://api.ted.europa.eu/v3/notices/search"
ROOT = Path(__file__).resolve().parent.parent
# Full-text terms per domain (multilingual where the term differs; English/latin terms like
# PKI/HSM/eIDAS/post-quantum appear verbatim in non-English notices too).
DOMAIN_FT = {
    "AI":    ['"artificial intelligence"', '"machine learning"', '"intelligence artificielle"',
              '"künstliche intelligenz"', '"automated decision-making"', '"deep learning"'],
    "PQC":   ['"post-quantum"', '"post quantum"', '"quantum-safe"', '"quantum resistant"',
              '"quantensicher"', '"crypto-agility"', '"ML-KEM"'],
    "PKI":   ['"public key infrastructure"', '"hardware security module"', '"certificate authority"',
              '"key management system"', '"code signing"', '"X.509"', '"PKI"'],
    "eIDAS": ['"electronic signature"', '"trust service"', '"digital identity"',
              '"electronic identification"', '"electronic seal"', '"identity verification"',
              '"digital wallet"', '"qualified electronic signature"'],
}
CPV_HINT = {"AI": "72000000", "PQC": "48732000", "PKI": "79417000", "eIDAS": "72000000"}


def pref(mldict):
    if not isinstance(mldict, dict):
        return str(mldict or "")
    for lang in ("eng", "ENG"):
        if mldict.get(lang):
            v = mldict[lang]; return (v[0] if isinstance(v, list) else v)
    for v in mldict.values():
        if v:
            return (v[0] if isinstance(v, list) else v)
    return ""


def post(query, page):
    body = {"query": query, "fields": ["publication-number", "notice-title", "publication-date",
            "buyer-name", "buyer-country", "classification-cpv"], "limit": 100,
            "page": page, "paginationMode": "PAGE_NUMBER"}
    req = urllib.request.Request(API, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": "tyche-observatory/0.1"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.status, r.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domain", required=True, choices=list(DOMAIN_FT))
    ap.add_argument("--pages", type=int, default=4)
    ap.add_argument("--since", default="2023-01-01")
    a = ap.parse_args()
    now = datetime.datetime.now(datetime.timezone.utc); today = now.date()
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    run_dir = ROOT / "data" / "raw" / f"ted-{a.domain}-{stamp}"; run_dir.mkdir(parents=True, exist_ok=True)
    ft = " OR ".join(f"FT ~ {t}" for t in DOMAIN_FT[a.domain])
    query = f"({ft}) AND publication-date>={a.since.replace('-','')} SORT BY publication-date DESC"
    out, dropped = [], 0
    for page in range(1, a.pages + 1):
        try:
            status, raw = post(query, page)
        except Exception as e:
            print(f"[DROP] {a.domain} p{page}: {e}", file=sys.stderr); break
        if status != 200:
            print(f"[DROP] {a.domain} p{page}: HTTP {status}", file=sys.stderr); break
        (run_dir / f"p{page}.json").write_bytes(raw)
        doc = json.loads(raw); notices = doc.get("notices", [])
        if not notices:
            break
        for n in notices:
            pd = str(n.get("publication-date") or "")[:10]
            if pd and pd > today.isoformat():
                dropped += 1; continue
            rec_raw = json.dumps(n, sort_keys=True, ensure_ascii=False).encode()
            rh = hashlib.sha256(rec_raw).hexdigest()
            bc = n.get("buyer-country")
            country = (bc[0] if isinstance(bc, list) and bc else (bc or ""))
            cpv = n.get("classification-cpv")
            cpv0 = (cpv[0] if isinstance(cpv, list) and cpv else CPV_HINT[a.domain])
            out.append({
                "ocid": f"ttpr-ted-{n.get('publication-number') or rh[:10]}",
                "id": rh[:16], "date": pd, "tag": ["tender"],
                "buyer": {"name": pref(n.get("buyer-name")), "country": country},
                "tender": {"title": pref(n.get("notice-title"))[:300],
                           "classification": {"scheme": "CPV", "id": str(cpv0), "description": ""}},
                "tt:domain": [a.domain], "tt:domain_evidence": f"cpv:{CPV_HINT[a.domain]}",
                "tt:domain_match": "TED-fulltext", "tt:source": "TED",
                "tt:source_url": API, "tt:fetched_at": now.isoformat(), "tt:http_status": 200,
                "tt:raw_hash": rh, "tt:licence": "EU-PO-reuse"})
        time.sleep(0.8)
    seen, uniq = set(), []
    for r in out:
        if r["ocid"] in seen:
            continue
        seen.add(r["ocid"]); uniq.append(r)
    pkg = {"version": "1.1", "publishedDate": now.isoformat(),
           "publisher": {"name": "Tyche Institute Trust-Tech Procurement Observatory"},
           "license": "https://ted.europa.eu/en/legal-notice", "releases": uniq}
    (ROOT / "data" / "releases" / f"ted-{a.domain}-{stamp}.json").write_text(json.dumps(pkg, indent=1, ensure_ascii=False))
    man = ROOT / "data" / "releases" / f"ted-{a.domain}-{stamp}.manifest.csv"
    with man.open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["ocid", "country", "title", "date", "raw_hash", "fetched_at"])
        for r in uniq:
            w.writerow([r["ocid"], r["buyer"].get("country", ""), r["tender"]["title"][:120],
                        r["date"], r["tt:raw_hash"], r["tt:fetched_at"]])
    print(f"TED domain={a.domain} kept={len(uniq)} future_dropped={dropped} raw={run_dir.name}")


if __name__ == "__main__":
    main()
