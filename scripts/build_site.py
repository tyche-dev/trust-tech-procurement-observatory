#!/usr/bin/env python3
"""Deterministic static-site builder for the Trust-Tech Procurement Observatory.

Reads ONLY the frozen consolidated dataset + analysis + findings and emits a static site:
an index.html (hero, headline finding, SVG charts, an interactive client-side record
explorer, method/trust, and citation) plus records-slim.json (for the explorer) and the
full dataset.json (for download). No network, no LLM, no hand-typed numbers — every figure
is computed from the committed data at build time. Re-run after every harvest.

Usage: python3 scripts/build_site.py [--out /srv/tyche/sites/procurement-eatf-eu]
"""
import argparse, datetime, html, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN_COLOR = {"AI": "#2563eb", "PKI": "#0f766e", "eIDAS": "#7c3aed", "PQC": "#b45309"}
DOMAINS = ["AI", "PKI", "eIDAS", "PQC"]
REGIONS = ["EU", "US", "Global", "UK"]
ZENODO = "10.5281/zenodo.21192405"
GH = "https://github.com/tyche-dev/trust-tech-procurement-observatory"


def esc(s):
    return html.escape(str(s or ""))


CSS = """
:root{
 --bg:#fbfaf7;--surface:#ffffff;--ink:#161b22;--muted:#5b6572;--soft:#8b94a0;
 --line:#e8e6df;--accent:#0f766e;--gap:#b45309;
 --ai:#2563eb;--pki:#0f766e;--eidas:#7c3aed;--pqc:#b45309;--maxw:1080px}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
 font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
 -webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 24px}
.serif{font-family:Georgia,"Iowan Old Style","Times New Roman",serif}
.nav{position:sticky;top:0;z-index:20;background:rgba(251,250,247,.86);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.nav .wrap{display:flex;align-items:center;gap:22px;height:56px}
.nav .brand{font-weight:700;letter-spacing:-.01em}
.nav .dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--accent);margin-right:8px}
.nav a.link{color:var(--muted);font-size:14px}.nav a.link:hover{color:var(--ink);text-decoration:none}
.nav .spacer{flex:1}
.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:6px 13px;font-size:13px;background:var(--surface);color:var(--ink)}
.hero{padding:64px 0 26px}
.hero h1{font-size:44px;line-height:1.08;letter-spacing:-.02em;margin:0 0 16px;max-width:16ch}
.hero .lede{font-size:19px;color:var(--muted);max-width:60ch;margin:0 0 30px}
.kbar{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:28px 0 8px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:18px 20px}
.kpi .n{font-size:34px;font-weight:800;letter-spacing:-.02em}
.kpi .l{color:var(--muted);font-size:13px;margin-top:2px}
.cta{display:flex;gap:12px;flex-wrap:wrap;margin-top:22px}
.btn{display:inline-block;border-radius:10px;padding:11px 18px;font-weight:600;font-size:15px;border:1px solid var(--accent)}
.btn.primary{background:var(--accent);color:#fff}.btn.primary:hover{text-decoration:none;filter:brightness(1.06)}
.btn.ghost{background:transparent;color:var(--accent)}
section{padding:46px 0;border-top:1px solid var(--line)}
.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:12px;font-weight:700;color:var(--accent);margin:0 0 10px}
h2{font-size:28px;letter-spacing:-.02em;margin:0 0 8px}
.sec-sub{color:var(--muted);max-width:65ch;margin:0 0 26px}
.finding{background:linear-gradient(180deg,#fff,#fdfbf6);border:1px solid var(--line);border-left:4px solid var(--gap);border-radius:16px;padding:30px 32px}
.finding .big{font-size:23px;line-height:1.35;font-weight:600;margin:0 0 6px}
.finding p{color:var(--muted);margin:14px 0 0;max-width:70ch}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:22px 24px}
.card h3{font-size:15px;margin:0 0 4px}.card .note{color:var(--soft);font-size:12.5px;margin:0 0 16px}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12.5px;color:var(--muted);margin-top:12px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px}
.heat{border-collapse:separate;border-spacing:4px;width:100%}
.heat th{font-size:11.5px;color:var(--muted);font-weight:600;text-align:center;padding:2px}
.heat td{text-align:center;border-radius:7px;color:#fff;font-weight:600;font-size:13px;padding:12px 6px;min-width:52px}
.heat td.z{background:#f0efe9;color:var(--soft);font-weight:500}
.heat .rl{color:var(--muted);font-weight:600;text-align:right;padding-right:8px;background:none}
.filters{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:16px}
.chip{border:1px solid var(--line);background:var(--surface);border-radius:999px;padding:7px 14px;font-size:13.5px;cursor:pointer;color:var(--muted);user-select:none}
.chip.on{color:#fff;border-color:transparent}
.chip[data-k=AI].on{background:var(--ai)}.chip[data-k=PKI].on{background:var(--pki)}
.chip[data-k=eIDAS].on{background:var(--eidas)}.chip[data-k=PQC].on{background:var(--pqc)}
.chip[data-r].on{background:var(--ink)}
#q{flex:1;min-width:180px;border:1px solid var(--line);border-radius:10px;padding:10px 14px;font-size:14px;background:var(--surface)}
#count{color:var(--muted);font-size:13px;margin:0 0 10px}
table.rec{width:100%;border-collapse:collapse;font-size:13.5px}
table.rec th{text-align:left;color:var(--muted);font-weight:600;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;padding:8px 10px;border-bottom:1px solid var(--line)}
table.rec td{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}
table.rec tr:hover{background:#faf9f4}
.dtag{display:inline-block;border-radius:5px;padding:1px 7px;font-size:11px;font-weight:700;color:#fff}
.ttl{max-width:40ch;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.more{display:block;margin:14px auto 0;border:1px solid var(--line);background:var(--surface);border-radius:10px;padding:9px 18px;font-size:14px;cursor:pointer;color:var(--ink)}
.steps{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
.step{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:18px 20px}
.step b{display:block;margin-bottom:4px}.step span{color:var(--muted);font-size:14px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:22px}
footer{border-top:1px solid var(--line);padding:34px 0 60px;color:var(--muted);font-size:13.5px}
@media(max-width:760px){.hero h1{font-size:34px}.kbar{grid-template-columns:1fr 1fr}
 .grid2,.cols,.steps{grid-template-columns:1fr}.nav a.link{display:none}}
"""


def hbar_svg(pairs, colorfn, w=440, unit="", maxlabel=16):
    mx = max((v for _, v in pairs), default=0) or 1
    rowh, pad, lblw = 34, 10, 118
    h = pad * 2 + rowh * len(pairs)
    bars = []
    for i, (lbl, v) in enumerate(pairs):
        y = pad + i * rowh
        bw = (w - lblw - 70) * v / mx
        bars.append(
            f'<text x="{lblw-8}" y="{y+rowh/2+4}" text-anchor="end" font-size="13" fill="#5b6572">{esc(lbl)[:maxlabel]}</text>'
            f'<rect x="{lblw}" y="{y+6}" width="{bw:.1f}" height="{rowh-14}" rx="4" fill="{colorfn(lbl)}"/>'
            f'<text x="{lblw+bw+7:.1f}" y="{y+rowh/2+4}" font-size="12.5" font-weight="700" fill="#161b22">{v:,}{unit}</text>')
    return f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" font-family="inherit">{"".join(bars)}</svg>'


def area_svg(pairs, w=460, h=200, color="#0f766e"):
    mx = max((v for _, v in pairs), default=0) or 1
    n = len(pairs); pl, pr, pt, pb = 34, 12, 14, 26
    iw, ih = w - pl - pr, h - pt - pb
    pts = [(pl + iw * i / (n - 1), pt + ih - ih * v / mx) for i, (_, v) in enumerate(pairs)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{pl},{pt+ih} " + line + f" {pl+iw},{pt+ih}"
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{color}"/>'
                   f'<text x="{x:.1f}" y="{y-8:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="#161b22">{pairs[i][1]:,}</text>'
                   for i, (x, y) in enumerate(pts))
    labs = "".join(f'<text x="{pl+iw*i/(n-1):.1f}" y="{h-6}" text-anchor="middle" font-size="11.5" fill="#8b94a0">{esc(l)}</text>'
                   for i, (l, _) in enumerate(pairs))
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" font-family="inherit">'
            f'<polygon points="{area}" fill="{color}" opacity="0.09"/>'
            f'<polyline points="{line}" fill="none" stroke="{color}" stroke-width="2.5"/>{dots}{labs}</svg>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/srv/tyche/sites/procurement-eatf-eu")
    a = ap.parse_args()
    ds = json.loads((ROOT / "data/consolidated/dataset.json").read_text())
    stats = json.loads((ROOT / "data/consolidated/stats.json").read_text())
    analysis = json.loads((ROOT / "data/consolidated/analysis.json").read_text())
    ff = sorted((ROOT / "results").glob("findings-*.json"))
    findings = json.loads(ff[-1].read_text()) if ff else None
    rels = ds.get("releases", [])
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    total = stats["unique_records"]; countries = stats["countries_covered"]

    slim = []
    for r in rels:
        b = r.get("buyer") or {}
        slim.append({"o": r.get("ocid", ""), "d": r.get("tt:domain", []), "s": r.get("tt:source", ""),
                     "c": b.get("country", "") or b.get("name", ""), "y": str(r.get("date", ""))[:10],
                     "t": (r.get("tender") or {}).get("title", "")[:180], "u": r.get("tt:source_url", "")})
    (out / "records-slim.json").write_text(json.dumps(slim, ensure_ascii=False, separators=(",", ":")))

    dom_bars = hbar_svg([(d, analysis["by_domain"].get(d, 0)) for d in
                         sorted(DOMAINS, key=lambda d: -analysis["by_domain"].get(d, 0))],
                        lambda d: DOMAIN_COLOR[d])
    trend = area_svg(sorted(analysis["by_year"].items()))
    ctry_bars = hbar_svg(list(stats["by_country"].items())[:12], lambda _: "#334155", maxlabel=20)

    mxrd = max(analysis["by_region_domain"].values()) or 1
    heat_rows = []
    for rg in REGIONS:
        cells = [f'<td class="rl">{rg}</td>']
        for d in DOMAINS:
            v = analysis["by_region_domain"].get(f"{rg}|{d}", 0)
            if v == 0:
                cells.append('<td class="z">0</td>')
            else:
                op = 0.30 + 0.70 * (math.log1p(v) / math.log1p(mxrd))
                cells.append(f'<td style="background:{DOMAIN_COLOR[d]};opacity:{op:.2f}">{v:,}</td>')
        heat_rows.append("<tr>" + "".join(cells) + "</tr>")
    heat = ('<table class="heat"><tr><th></th>' + "".join(f"<th>{d}</th>" for d in DOMAINS) + "</tr>"
            + "".join(heat_rows) + "</table>")
    dom_legend = "".join(f'<span><i style="background:{DOMAIN_COLOR[d]}"></i>{d}</span>' for d in DOMAINS)

    pqc = analysis["pqc_gap"]
    finding_big = (findings.get("pqc_gap_headline") if findings else
                   f"PQC appears in just {pqc['overall']['count']} of {total:,} records ({pqc['overall']['pct']}%).")
    tot_dom = sum(analysis["by_domain"].values()) or 1
    segs = "".join(
        f'<div style="width:{100*analysis["by_domain"][d]/tot_dom:.2f}%;background:{DOMAIN_COLOR[d]}" title="{d}: {analysis["by_domain"][d]:,}"></div>'
        for d in sorted(DOMAINS, key=lambda d: -analysis["by_domain"].get(d, 0)))
    share_bar = f'<div style="display:flex;height:26px;border-radius:8px;overflow:hidden;margin:18px 0 6px">{segs}</div>'

    js = """
const R=await (await fetch('records-slim.json')).json();
const DC={AI:'#2563eb',PKI:'#0f766e',eIDAS:'#7c3aed',PQC:'#b45309'};
const REG={USAspending:'US',FPDS:'US','UK-ContractsFinder':'UK','UK-FTS':'UK',TED:'EU',WorldBank:'Global','IE-CKAN':'IE'};
let doms=new Set(),regs=new Set(),q='',shown=50;
const el=id=>document.getElementById(id);
function match(r){
 if(doms.size&&!r.d.some(d=>doms.has(d)))return false;
 if(regs.size&&!regs.has(REG[r.s]||r.s))return false;
 if(q&&!((r.t+' '+r.c).toLowerCase().includes(q)))return false;
 return true;}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}
function render(){
 const f=R.filter(match);
 el('count').textContent=f.length.toLocaleString()+' of '+R.length.toLocaleString()+' records';
 el('rows').innerHTML=f.slice(0,shown).map(r=>{
  const tags=r.d.map(d=>`<span class="dtag" style="background:${DC[d]||'#666'}">${d}</span>`).join(' ');
  const src=r.u?`<a href="${esc(r.u)}" target="_blank" rel="noopener">${esc(r.s)}</a>`:esc(r.s);
  return `<tr><td>${esc(r.y)}</td><td>${tags}</td><td class="ttl" title="${esc(r.t)}">${esc(r.t)}</td><td>${esc(r.c)}</td><td>${src}</td></tr>`;}).join('');
 el('more').style.display=(f.length>shown)?'block':'none';}
document.querySelectorAll('.chip').forEach(c=>c.onclick=()=>{
 const k=c.dataset.k,r=c.dataset.r;c.classList.toggle('on');
 if(k){doms.has(k)?doms.delete(k):doms.add(k);}
 if(r){regs.has(r)?regs.delete(r):regs.add(r);}
 shown=50;render();});
el('q').oninput=e=>{q=e.target.value.toLowerCase();shown=50;render();};
el('more').onclick=()=>{shown+=100;render();};
render();
"""
    dom_chips = "".join(f'<span class="chip" data-k="{d}">{d}</span>' for d in DOMAINS)
    reg_chips = "".join(f'<span class="chip" data-r="{r}">{r}</span>' for r in REGIONS)
    findings_paras = ""
    if findings:
        for p in findings.get("paragraphs", []):
            findings_paras += f'<h3 style="font-size:16px;margin:22px 0 4px">{esc(p.get("title",""))}</h3>{p.get("html","")}'

    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trust-Tech Procurement Observatory — Tyche Institute</title>
<meta name="description" content="What governments worldwide procure across AI, post-quantum cryptography, PKI and eIDAS/digital identity — a live, provenance-verified dataset. {total:,} records, {countries} countries.">
<meta property="og:title" content="Trust-Tech Procurement Observatory">
<meta property="og:description" content="{total:,} provenance-verified government procurement records across AI, PQC, PKI and digital identity, from {countries} countries.">
<style>{CSS}</style></head><body>

<nav class="nav"><div class="wrap">
 <span class="brand"><span class="dot"></span>Trust-Tech Procurement Observatory</span>
 <span class="spacer"></span>
 <a class="link" href="#finding">Finding</a><a class="link" href="#glance">Data</a>
 <a class="link" href="#explore">Explore</a><a class="link" href="#method">Method</a>
 <a class="link" href="#cite">Cite</a>
</div></nav>

<header class="hero"><div class="wrap">
 <p class="pill">Live &middot; build {now} &middot; Tyche Institute</p>
 <h1 class="serif">What the world's governments buy to build digital trust</h1>
 <p class="lede">A live, provenance-verified dataset of public-sector procurement across four
 trust-technology domains: artificial intelligence, post-quantum cryptography, public-key
 infrastructure, and eIDAS / digital identity. Every record traces to a live government or
 inter-governmental procurement API. A record with no verifiable source cannot exist here.</p>
 <div class="kbar">
  <div class="kpi"><div class="n">{total:,}</div><div class="l">unique records</div></div>
  <div class="kpi"><div class="n">{countries}</div><div class="l">countries</div></div>
  <div class="kpi"><div class="n">4</div><div class="l">domains</div></div>
  <div class="kpi"><div class="n">4</div><div class="l">public sources</div></div>
 </div>
 <div class="cta"><a class="btn primary" href="#explore">Explore the records</a>
  <a class="btn ghost" href="#cite">Cite the dataset</a></div>
</div></header>

<section id="finding"><div class="wrap">
 <p class="eyebrow">Headline finding</p><h2>The post-quantum procurement gap</h2>
 <div class="finding">
  <p class="big serif">{esc(finding_big)}</p>{share_bar}
  <div class="legend">{dom_legend}<span style="margin-left:auto;color:#8b94a0">domain share of {tot_dom:,} tagged records</span></div>
  <p>Governments have finalized post-quantum standards (NIST FIPS 203, 204, 205 in 2024) and set
  migration deadlines running 2030&ndash;2033 (NSA CNSA 2.0), yet quantum-safe cryptography is the
  smallest domain in the dataset by a wide margin: {pqc['US']['count']} of {pqc['US']['total']} US
  records ({pqc['US']['pct']}%), {pqc['EU']['count']} of {pqc['EU']['total']} EU records ({pqc['EU']['pct']}%),
  and {pqc['Global']['count']} of {pqc['Global']['total']} World Bank records ({pqc['Global']['pct']}%).
  The mandate exists; the procurement signal is, so far, almost invisible.</p>
 </div>
</div></section>

<section id="glance"><div class="wrap">
 <p class="eyebrow">At a glance</p><h2>Coverage across domains, regions, time and place</h2>
 <p class="sec-sub">Every figure is computed at build time from the committed dataset. Cross-region
 comparisons are comparisons of <em>visible</em> procurement, not of total national spend.</p>
 <div class="grid2">
  <div class="card"><h3>Records by domain</h3><p class="note">All sources combined</p>{dom_bars}</div>
  <div class="card"><h3>Region &times; domain</h3><p class="note">Cell = record count; colour by domain, intensity by volume</p>{heat}<div class="legend">{dom_legend}</div></div>
  <div class="card"><h3>Records by year</h3><p class="note">2026 is year-to-date; totals shaped by source publication windows</p>{trend}</div>
  <div class="card"><h3>Top countries</h3><p class="note">EU dominance reflects TED's near-complete above-threshold coverage, not that these countries buy the most</p>{ctry_bars}</div>
 </div>
</div></section>

<section id="explore"><div class="wrap">
 <p class="eyebrow">Explore</p><h2>Browse the records</h2>
 <p class="sec-sub">Filter by domain and region, or search titles and buyers. Every row links to its
 live source notice. This runs entirely in your browser over the published dataset.</p>
 <div class="filters">{dom_chips}<span style="width:10px"></span>{reg_chips}</div>
 <div class="filters"><input id="q" placeholder="Search title or buyer / country…"></div>
 <p id="count"></p>
 <table class="rec"><thead><tr><th>Date</th><th>Domain</th><th>Title</th><th>Buyer / country</th><th>Source</th></tr></thead>
 <tbody id="rows"></tbody></table>
 <button id="more" class="more">Show more</button>
</div></section>

<section id="findings-detail"><div class="wrap">
 <p class="eyebrow">Findings</p><h2>What the data says</h2>
 <p class="sec-sub">{esc(findings.get('lead','')) if findings else ''}</p>
 {findings_paras}
 <p style="color:#8b94a0;font-size:13px;margin-top:18px">{esc(findings.get('provenance','')) if findings else ''}</p>
</div></section>

<section id="method"><div class="wrap">
 <p class="eyebrow">Method &middot; why you can trust these numbers</p>
 <h2>Anti-fabrication by construction</h2>
 <p class="sec-sub">This observatory's predecessor was compromised by an automated pipeline that
 fabricated sources. This one is built so that fabrication is structurally impossible.</p>
 <div class="steps">
  <div class="step"><b>Live-fetch-or-drop</b><span>A record exists only if a harvest script received an HTTP&nbsp;200 from a listed source this run. No manual insertion, no language model in the harvest loop.</span></div>
  <div class="step"><b>Provenance-required</b><span>Every record carries its source URL, fetch timestamp, HTTP status, and a sha256 hash of the raw upstream payload. Missing any of these, it is rejected at write time.</span></div>
  <div class="step"><b>Validated</b><span>A validator hard-fails on future dates, placeholder hosts, invented classification codes, and any count that cannot be re-derived from the committed records.</span></div>
  <div class="step"><b>Reproducible</b><span>The full harvest, validation, consolidation and analysis pipeline is open, with no third-party dependencies. Re-run it and reproduce every number.</span></div>
 </div>
</div></section>

<section id="cite"><div class="wrap">
 <p class="eyebrow">Data &amp; citation</p><h2>Open data, openly licensed</h2>
 <div class="cols">
  <div class="card"><h3>Cite this dataset</h3><p class="note">CC-BY-4.0 &middot; versioned on Zenodo</p>
   <p>Sokolov, A. (2026). <em>The Trust-Tech Procurement Observatory</em>. Zenodo. <a href="https://doi.org/{ZENODO}">{ZENODO}</a></p>
   <p style="margin-top:14px"><a class="btn ghost" href="https://doi.org/{ZENODO}">Zenodo record</a>
   <a class="btn ghost" href="dataset.json" download>Download dataset.json</a></p></div>
  <div class="card"><h3>Code &amp; descriptor</h3><p class="note">Full pipeline + data descriptor</p>
   <p>Harvesters, validator, consolidation and analysis code, plus the data descriptor, are public on GitHub.</p>
   <p style="margin-top:14px"><a class="btn ghost" href="{GH}">GitHub repository</a>
   <a class="btn ghost" href="{GH}/raw/main/data-descriptor.pdf">Data descriptor (PDF)</a></p></div>
 </div>
 <p style="color:#8b94a0;font-size:13px;margin-top:20px">Source attribution: EU TED (EU Publications
 Office reuse) &middot; US USAspending (public domain) &middot; UK Contracts Finder / Find-a-Tender
 (OGL v3.0) &middot; World Bank procurement notices (open).</p>
</div></section>

<footer><div class="wrap">
 <strong>Trust-Tech Procurement Observatory</strong> &middot; built deterministically from the
 committed dataset, {now} &middot; <a href="https://tyche.institute">Tyche Institute</a>, Tallinn,
 Estonia &middot; sibling: <a href="https://obscure-ai.eatf.eu">obscure-ai</a>.
</div></footer>

<script type="module">{js}</script>
</body></html>"""

    (out / "index.html").write_text(page)
    (out / ".nojekyll").write_text("")
    (out / "robots.txt").write_text("User-agent: *\nAllow: /\n")
    (out / "dataset.json").write_text(json.dumps(ds, separators=(",", ":"), ensure_ascii=False))
    (out / "stats.json").write_text(json.dumps(stats, indent=1, ensure_ascii=False))
    print(f"built site: {out} ({total:,} records, {countries} countries, {len(slim)} explorer rows)")


if __name__ == "__main__":
    main()
