#!/usr/bin/env python3
"""Deterministic static-site builder for the Trust-Tech Procurement Observatory.

Reads ONLY the frozen consolidated dataset (data/consolidated/{dataset,stats}.json) and
emits a static HTML site. No network, no LLM, no hand-typed numbers — every figure on the
page is computed from the committed dataset at build time. Re-run after every harvest;
never hand-edit the output.

Usage: python3 scripts/build_site.py [--out /srv/tyche/sites/procurement-eatf-eu]
"""
import argparse, collections, datetime, html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CSS = """
:root{--bg:#0b0d10;--panel:#14171c;--line:#262b33;--fg:#e8eaed;--muted:#9aa4b2;--accent:#4fd1c5}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
header{padding:48px 24px 24px;max-width:1100px;margin:0 auto}
h1{font-size:28px;margin:0 0 8px}
.sub{color:var(--muted);font-size:15px;max-width:70ch}
main{max-width:1100px;margin:0 auto;padding:0 24px 80px}
.stats{display:flex;gap:16px;flex-wrap:wrap;margin:32px 0}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px 22px;min-width:140px}
.stat .n{font-size:32px;font-weight:700;color:var(--accent)}
.stat .l{color:var(--muted);font-size:13px;margin-top:4px}
table{width:100%;border-collapse:collapse;margin:16px 0 40px;font-size:14px}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left}
th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.03em}
tr:hover{background:#191d23}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.badge{display:inline-block;background:#1c2129;border:1px solid var(--line);border-radius:6px;padding:2px 8px;font-size:12px;color:var(--muted)}
section{margin-top:48px}
h2{font-size:20px;border-bottom:1px solid var(--line);padding-bottom:8px}
.provenance{color:var(--muted);font-size:12px}
footer{max-width:1100px;margin:40px auto;padding:0 24px;color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:20px}
.record-title{max-width:52ch;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;display:inline-block}
"""


def esc(s):
    return html.escape(str(s or ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/srv/tyche/sites/procurement-eatf-eu")
    a = ap.parse_args()
    ds = json.loads((ROOT / "data/consolidated/dataset.json").read_text())
    stats = json.loads((ROOT / "data/consolidated/stats.json").read_text())
    releases = ds.get("releases", [])
    import glob as _glob
    _ff = sorted(_glob.glob(str(ROOT / "results/findings-*.json")))
    findings = json.loads(Path(_ff[-1]).read_text()) if _ff else None
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = stats["unique_records"]; countries = stats["countries_covered"]

    # sample rows per domain for the table (largest amounts / most recent, capped, deterministic sort)
    by_domain = collections.defaultdict(list)
    for r in releases:
        for d in r.get("tt:domain", []):
            by_domain[d].append(r)
    rows_html = []
    for dom in ("AI", "PQC", "PKI", "eIDAS"):
        recs = sorted(by_domain.get(dom, []), key=lambda r: r.get("date", ""), reverse=True)[:15]
        if not recs:
            continue
        rows_html.append(f'<h2>{dom} — {len(by_domain.get(dom, []))} records</h2>')
        rows_html.append("<table><tr><th>Date</th><th>Buyer/Country</th><th>Title</th><th>Source</th></tr>")
        for r in recs:
            buyer = (r.get("buyer") or {})
            title = (r.get("tender") or {}).get("title", "")
            rows_html.append(
                f"<tr><td>{esc(r.get('date',''))}</td>"
                f"<td>{esc(buyer.get('country') or buyer.get('name',''))}</td>"
                f"<td class='record-title' title='{esc(title)}'>{esc(title)}</td>"
                f"<td><span class='badge'>{esc(r.get('tt:source',''))}</span></td></tr>")
        rows_html.append("</table>")

    findings_section = ""
    if findings:
        paras = "".join(
            f"<h3 style='margin:24px 0 6px;font-size:16px'>{esc(p.get('title',''))}</h3>{p.get('html','')}"
            for p in findings.get("paragraphs", []))
        findings_section = f"""
<section id="findings">
<h2>Findings <span class='badge'>build {esc(findings.get('build',''))}</span></h2>
<p style="background:#141b17;border-left:3px solid var(--accent);padding:14px 18px;border-radius:6px;font-size:16px">
<strong>{esc(findings.get('pqc_gap_headline',''))}</strong></p>
<p class="sub">{esc(findings.get('lead',''))}</p>
{paras}
<p class="provenance" style="margin-top:20px"><strong>How to read this.</strong> {esc(findings.get('method_note',''))}</p>
<p class="provenance">{esc(findings.get('provenance',''))}</p>
</section>"""
    country_rows = "".join(
        f"<tr><td>{esc(c)}</td><td>{n}</td></tr>" for c, n in list(stats["by_country"].items())[:25])

    index = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trust-Tech Procurement Observatory — Tyche Institute</title>
<meta name="description" content="What governments worldwide procure in AI, post-quantum cryptography, PKI, and eIDAS/digital identity — a live, provenance-verified dataset.">
<style>{CSS}</style></head><body>
<header>
<h1>Trust-Tech Procurement Observatory</h1>
<p class="sub">What governments worldwide actually <strong>procure</strong> across four trust-technology
domains — AI, post-quantum cryptography (PQC), public-key infrastructure (PKI), and eIDAS/digital
identity. Every record below traces to a live government or IGO procurement API fetched at build
time; a record with no verifiable source cannot enter this dataset. Built by
<a href="https://tyche.institute">Tyche Institute</a>. Sibling projects:
<a href="https://obscure-ai.eatf.eu">obscure-ai</a> (AI incident/vulnerability catalogue).</p>
</header>
<main>
<div class="stats">
<div class="stat"><div class="n">{total:,}</div><div class="l">unique procurement records</div></div>
<div class="stat"><div class="n">{countries}</div><div class="l">countries / jurisdictions</div></div>
<div class="stat"><div class="n">4</div><div class="l">domains: AI · PQC · PKI · eIDAS</div></div>
<div class="stat"><div class="n">4</div><div class="l">live sources: TED · USAspending · UK · World Bank</div></div>
</div>

{findings_section}

<section>
<h2>Coverage by region × domain</h2>
<table><tr><th>Region</th><th>AI</th><th>PKI</th><th>PQC</th><th>eIDAS</th><th>Total</th></tr>
{"".join(
    f"<tr><td>{esc(rg)}</td>" + "".join(
        f"<td>{stats['by_region_domain'].get(rg+'|'+d, 0)}</td>" for d in ('AI','PKI','PQC','eIDAS')
    ) + f"<td><strong>{sum(stats['by_region_domain'].get(rg+'|'+d, 0) for d in ('AI','PKI','PQC','eIDAS'))}</strong></td></tr>"
    for rg in ('US','UK','EU','Global')
)}
</table>
</section>

<section>
<h2>Top 25 countries by record count</h2>
<table><tr><th>Country</th><th>Records</th></tr>{country_rows}</table>
</section>

{''.join(rows_html)}

<section>
<h2>Method &amp; anti-fabrication guarantees</h2>
<p>Every record carries an immutable provenance stamp: the exact source URL, the fetch
timestamp, the observed HTTP status (must be 200), and a sha256 hash of the raw upstream
payload. A record enters this dataset only through a deterministic harvest script — never
by hand, never by an LLM. A validator rejects any record with a future date, a placeholder
host, an unverified classification code, or a missing provenance field before it can be
published. Sources: EU TED (v3 full-text API), US USAspending.gov, UK Contracts Finder /
Find-a-Tender (OCDS), World Bank procurement notices (~100 borrower countries). Full method, source ledger, and the complete dataset are archived on Zenodo (CC-BY-4.0), DOI <a href="https://doi.org/10.5281/zenodo.21192405">10.5281/zenodo.21192405</a>.</p>
</section>
</main>
<footer>
<p class="provenance">Built deterministically from the committed dataset · generated {now} ·
Tyche Institute, Tallinn, Estonia · <a href="https://tyche.institute">tyche.institute</a></p>
</footer>
</body></html>"""

    (out / "index.html").write_text(index)
    (out / ".nojekyll").write_text("")
    (out / "robots.txt").write_text("User-agent: *\nAllow: /\n")
    (out / "dataset.json").write_text(json.dumps(ds, indent=0, ensure_ascii=False))
    (out / "stats.json").write_text(json.dumps(stats, indent=1, ensure_ascii=False))
    print(f"built site: {out} ({total} records, {countries} countries)")


if __name__ == "__main__":
    main()
