#!/usr/bin/env python3
"""Deposit the Trust-Tech Procurement Observatory v0 dataset to Zenodo.

Mirrors the established Tyche deposit pattern: create draft -> upload files -> set metadata
-> (optionally) publish. Draft-only unless --publish is passed.
"""
import argparse, hashlib, json, os, pathlib, ssl, urllib.error, urllib.parse, urllib.request
try:
    import certifi
except Exception:
    certifi = None

VAULT = pathlib.Path("/srv/tyche/repos/tyche-research-vault")
PROJ = pathlib.Path("/srv/tyche/projects/trust-tech-procurement-observatory")
DEP = PROJ / "deposit"
ARCHIVE = DEP / "trust-tech-procurement-observatory-v0-2026-07-04.tar.gz"
SHA_FILE = DEP / "trust-tech-procurement-observatory-v0-2026-07-04.tar.gz.sha256"
DATASET = PROJ / "data/consolidated/dataset.json"
README = DEP / "trust-tech-procurement-observatory-v0/README.md"
RECORD_MD = PROJ / "results/ZENODO-DEPOSIT-RECORD-2026-07-04.md"
BASE = "https://zenodo.org/api"
COMMUNITY = "tyche-institute"   # Tyche Zenodo Community (best-effort; ignored if unknown)

DESCRIPTION = """
<p>The <strong>Trust-Tech Procurement Observatory</strong> is a live, provenance-verified dataset
of what governments worldwide procure across four trust-technology domains: artificial
intelligence (AI), post-quantum cryptography (PQC), public-key infrastructure (PKI), and
eIDAS/digital identity. This v0 release (build 2026-07-04) holds 4,401 unique procurement
records spanning 106 countries, harvested from four public sources: EU TED, US USAspending,
UK Contracts Finder / Find-a-Tender, and World Bank procurement notices.</p>
<p><strong>Anti-fabrication by construction.</strong> Every record carries an immutable provenance
stamp (source URL, fetch timestamp, HTTP status, and a sha256 hash of the raw upstream payload).
A record enters the corpus only through a deterministic harvest script that received an HTTP 200
from a listed source; there is no manual-insertion path and no language model in the harvest loop.
A validator rejects any record with a future date, a placeholder host, an unverified
classification code, or a missing provenance field.</p>
<p><strong>Headline finding &mdash; the post-quantum procurement gap.</strong> PQC appears in only 50
of 4,401 records (1.14%): 3.03% of the US slice, 1.0% of the EU slice, and 0% of the World Bank
development-finance slice, despite finalized NIST PQC standards (FIPS 203/204/205, 2024) and NSA
CNSA 2.0 migration deadlines running 2030&ndash;2033.</p>
<p>The archive contains the consolidated OCDS-1.1-aligned dataset, all computed statistics, the
verified findings narrative, the source ledger, and the full harvest/validate/consolidate/analyze
pipeline (dependency-free Python). Sources: EU TED (EU Publications Office reuse), USAspending
(US public domain), UK Contracts Finder/FTS (OGL v3.0), World Bank (open). Released CC-BY-4.0 with
per-source attribution preserved. Live site: https://procurement.eatf.eu</p>
""".strip()

FILES = [
    ("trust-tech-procurement-observatory-v0-2026-07-04.tar.gz", ARCHIVE),
    ("trust-tech-procurement-observatory-v0-2026-07-04.tar.gz.sha256", SHA_FILE),
    ("dataset.json", DATASET),
    ("README.md", README),
]


def load_token():
    env = VAULT / ".env"
    for line in env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    tok = os.environ.get("ZENODO_TOKEN", "")
    if not tok:
        raise SystemExit("ZENODO_TOKEN not set")
    return tok


def req(method, url, token, data=None, ctype=None):
    headers = {"Authorization": f"Bearer {token}"}
    body = None
    if isinstance(data, dict):
        body = json.dumps(data).encode(); headers["Content-Type"] = "application/json"
    elif isinstance(data, (bytes, bytearray)):
        body = bytes(data); headers["Content-Type"] = ctype or "application/octet-stream"
    ctx = ssl.create_default_context(cafile=certifi.where()) if certifi else None
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=body, method=method, headers=headers),
                                    timeout=300, context=ctx) as r:
            raw = r.read(); return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f"{method} {url} -> HTTP {e.code}\n{e.read().decode(errors='replace')}")


def metadata():
    return {"metadata": {
        "title": "The Trust-Tech Procurement Observatory: a provenance-verified dataset of government demand for AI, post-quantum cryptography, PKI and digital identity",
        "upload_type": "dataset", "description": DESCRIPTION,
        "creators": [{"name": "Sokolov, Anton", "affiliation": "Tyche Institute, Tallinn, Estonia",
                      "orcid": "0000-0003-2452-7096"}],
        "publication_date": "2026-07-04", "version": "v0-2026-07-04",
        "access_right": "open", "license": "cc-by-4.0", "language": "eng",
        "keywords": ["public procurement", "artificial intelligence", "post-quantum cryptography",
                     "PKI", "eIDAS", "digital identity", "open contracting", "OCDS", "government demand",
                     "provenance", "reproducibility", "trust technology"],
        "notes": "Archive SHA-256: " + ARCHIVE_SHA + ". Live observatory: https://procurement.eatf.eu . "
                 "Every reported statistic is computed by scripts/analyze.py and re-verified against the raw dataset.",
    }}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


ARCHIVE_SHA = ""


def main():
    global ARCHIVE_SHA
    ap = argparse.ArgumentParser(); ap.add_argument("--publish", action="store_true"); a = ap.parse_args()
    for _, p in FILES:
        if not p.exists():
            raise SystemExit(f"missing: {p}")
    ARCHIVE_SHA = sha256(ARCHIVE)
    token = load_token()
    dep = req("POST", f"{BASE}/deposit/depositions", token, data={})
    dep_id = dep["id"]; bucket = dep["links"]["bucket"]
    print(f"draft_id={dep_id}")
    for name, p in FILES:
        body = p.read_bytes()
        req("PUT", f"{bucket}/{urllib.parse.quote(name)}", token, data=body, ctype="application/octet-stream")
        print(f"uploaded={name} bytes={len(body)}")
    req("PUT", f"{BASE}/deposit/depositions/{dep_id}", token, data=metadata())
    print("metadata=updated")
    if not a.publish:
        print(f"draft=https://zenodo.org/deposit/{dep_id}")
        print("NOT_PUBLISHED (pass --publish to mint the DOI)")
        return 0
    pub = req("POST", f"{BASE}/deposit/depositions/{dep_id}/actions/publish", token)
    doi = pub.get("doi") or pub.get("metadata", {}).get("doi")
    concept = pub.get("conceptdoi") or pub.get("metadata", {}).get("conceptrecid")
    url = pub.get("links", {}).get("html") or f"https://zenodo.org/records/{pub.get('id')}"
    RECORD_MD.write_text("\n".join([
        "# Trust-Tech Procurement Observatory — Zenodo deposit record",
        f"- Record ID: {pub.get('id')}", f"- Version DOI: {doi}", f"- Concept DOI: {concept}",
        f"- URL: {url}", f"- Archive SHA-256: {ARCHIVE_SHA}", "- Licence: CC-BY-4.0",
        "- Version: v0-2026-07-04", "",
    ]) + "\n")
    print(f"published doi={doi} url={url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
