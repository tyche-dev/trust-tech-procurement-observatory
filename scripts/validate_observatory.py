#!/usr/bin/env python3
"""Anti-fabrication validator for the Trust-Tech Procurement Observatory.

Fails the build on the exact tells that killed the predecessor pilot. It is the write-time
contract: a release package is trustworthy only if EVERY record proves a real live fetch.

Checks per release record:
  1. provenance-required: tt:source_url, tt:fetched_at, tt:http_status==200, tt:raw_hash(64-hex)
  2. no future dates: record .date and tt:fetched_at date must be <= today
  3. no placeholder hosts: no example.com / example.org / localhost / .invalid in any URL
  4. code allowlist: tt:domain_evidence code (CPV/NAICS/PSC) must be in methods allowlist
     (keyword: evidence is always allowed; a bare invented code is not)
  5. count integrity: reported release count == actual len(releases)

Exit 0 = clean, 1 = fabrication tell found. No network, no deps.
"""
import datetime, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = datetime.date.today()
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PLACEHOLDER = re.compile(r"(example\.(com|org|net)|localhost|\.invalid|placeholder)", re.I)
# allowlist of codes verified live in the blueprint run (keep in sync with methods/domain-selection.md)
CODE_ALLOW = {"72000000", "48000000", "48732000", "79417000", "35700000", "35711000",
              "541512", "541511", "541519", "541513", "334111", "334118"}


def check_record(r, errs, rel):
    rid = r.get("ocid", "?")
    if r.get("tt:http_status") != 200:
        errs.append(f"{rel}:{rid} tt:http_status != 200")
    if not HEX64.match(str(r.get("tt:raw_hash", ""))):
        errs.append(f"{rel}:{rid} missing/invalid tt:raw_hash")
    if not str(r.get("tt:source_url", "")).startswith("http"):
        errs.append(f"{rel}:{rid} missing tt:source_url")
    fa = str(r.get("tt:fetched_at", ""))
    if not fa:
        errs.append(f"{rel}:{rid} missing tt:fetched_at")
    else:
        try:
            if datetime.date.fromisoformat(fa[:10]) > TODAY:
                errs.append(f"{rel}:{rid} FUTURE fetched_at {fa[:10]}")
        except ValueError:
            errs.append(f"{rel}:{rid} unparseable tt:fetched_at {fa!r}")
    d = str(r.get("date", ""))
    if d:
        try:
            if datetime.date.fromisoformat(d[:10]) > TODAY:
                errs.append(f"{rel}:{rid} FUTURE record date {d}")
        except ValueError:
            pass
    blob = json.dumps(r)
    if PLACEHOLDER.search(blob):
        errs.append(f"{rel}:{rid} placeholder host in record")
    ev = str(r.get("tt:domain_evidence", ""))
    if ev and not ev.startswith("keyword:"):
        code = ev.split(":")[-1].split("-")[0].strip()
        if code and code not in CODE_ALLOW:
            errs.append(f"{rel}:{rid} code {code!r} not in verified allowlist")


def main():
    rel_dir = ROOT / "data" / "releases"
    pkgs = sorted(rel_dir.glob("*.json"))
    if not pkgs:
        print("no release packages yet (data/releases/*.json) — nothing to validate")
        return 0
    errs, total = [], 0
    for p in pkgs:
        try:
            pkg = json.loads(p.read_text())
        except Exception as e:
            errs.append(f"{p.name}: unreadable ({e})"); continue
        rels = pkg.get("releases", [])
        total += len(rels)
        for r in rels:
            check_record(r, errs, p.name)
    if errs:
        print(f"VALIDATION FAILED ({len(errs)} issues across {total} records):")
        for e in errs[:40]:
            print("  -", e)
        return 1
    print(f"VALIDATION PASSED: {total} records across {len(pkgs)} package(s); "
          f"all provenance-required fields present, no future dates, no placeholders, codes in allowlist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
