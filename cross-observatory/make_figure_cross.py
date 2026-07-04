#!/usr/bin/env python3
"""Cross-observatory figure: the trust-stack demand results (RQ-1, RQ-3, RQ-4).
Strict black-on-white. Values from results/cross-observatory-findings.json + the analyses.
"""
import csv
import json
import collections
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator

HERE = Path(__file__).resolve().parent
F = json.loads((HERE / "results/cross-observatory-findings.json").read_text())

plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 10, "axes.edgecolor": "black",
                     "text.color": "black", "axes.labelcolor": "black", "xtick.color": "black",
                     "ytick.color": "black", "figure.facecolor": "white", "axes.facecolor": "white"})
fig, ax = plt.subplots(1, 3, figsize=(9.6, 3.4))
for a in ax:
    a.spines[["top", "right"]].set_visible(False)

# Panel A: RQ-1 cliff — quantum-vulnerable trust procurement vs quantum-safe
r1 = F["RQ1_quantum_trust_cliff"]
qv = r1["quantum_vulnerable_trust_procurement_PKI_plus_eIDAS"]; pqc = r1["pqc_procurement_matched"]; pqcc = r1["pqc_procurement_confirmed"]
bars = ax[0].bar(["PKI+eIDAS\n(vulnerable)", "PQC\n(safe)"], [qv, pqc], width=0.6,
                 facecolor="white", edgecolor="black", hatch=["", "////"], linewidth=1.1)
ax[0].set_yscale("log"); ax[0].set_ylim(1, 6000); ax[0].yaxis.set_major_locator(FixedLocator([1, 10, 100, 1000]))
ax[0].set_ylabel("procurement records (log)")
ax[0].set_title("A. RQ-1: the quantum-trust cliff", fontsize=9.6, loc="left", pad=8)
ax[0].text(0, qv * 1.3, f"{qv:,}", ha="center", fontsize=8.5)
ax[0].text(1, pqc * 1.35, f"{pqc}", ha="center", fontsize=8.5)
ax[0].annotate(f"{r1['cliff_ratio_matched']:.0f}x\n(confirmed {r1['cliff_ratio_confirmed']:.0f}x)",
               xy=(1, pqc * 1.05), xytext=(0.45, 900), fontsize=8.2, ha="center",
               arrowprops=dict(arrowstyle="->", color="black", lw=0.8))

# Panel B: RQ-3 decoupling — AI procurement vs incidents per country
import importlib.util
spec = importlib.util.spec_from_file_location("la", HERE / "link_analysis.py")
la = importlib.util.module_from_spec(spec); spec.loader.exec_module(la)
rels = la.load_procurement()
aic = collections.Counter()
for r in rels:
    c = la.iso2((r.get("buyer") or {}).get("country", ""))
    if "AI" in r.get("tt:domain", []) and c:
        aic[c] += 1
inc = collections.Counter()
for x in la.load_incidents():
    c = la.iso2(x.get("jurisdiction", ""))
    if c:
        inc[c] += 1
common = sorted(set(aic) & set(inc))
xs = [aic[c] for c in common]; ys = [inc[c] for c in common]
ax[1].scatter(xs, ys, s=22, facecolor="white", edgecolor="black", linewidth=1.0)
for c in common:
    if aic[c] > 40 or inc[c] > 40:
        ax[1].annotate(c, (aic[c], inc[c]), fontsize=7.5, xytext=(3, 2), textcoords="offset points")
ax[1].set_xscale("symlog"); ax[1].set_yscale("symlog")
ax[1].set_xlabel("AI procurement records"); ax[1].set_ylabel("AI incidents (obscure-ai)")
ax[1].set_title("B. RQ-3: demand vs risk (decoupled)", fontsize=9.6, loc="left", pad=8)
ax[1].text(0.98, 0.06, f"Spearman rho = {F['RQ3_demand_risk_alignment']['spearman_rho_demand_vs_incidents']}",
           transform=ax[1].transAxes, ha="right", fontsize=8)

# Panel C: RQ-4 assurance gap — assured share of base, per layer
r4 = F["RQ4_assurance_gap"]
labels = ["Crypto\n(PQC/PKI+eIDAS)", "AI\n(assurance kw)"]
vals = [100 * r4["crypto_layer_assurance_ratio_PQC_over_PKIeIDAS"], 100 * r4["ai_layer_assurance_keyword_share"]]
b = ax[2].bar(labels, vals, width=0.55, facecolor="white", edgecolor="black", hatch="////", linewidth=1.1)
ax[2].set_ylim(0, 8); ax[2].set_ylabel("assured share of base (%)")
ax[2].set_title("C. RQ-4: the assurance gap", fontsize=9.6, loc="left", pad=8)
for r, v in zip(b, vals):
    ax[2].text(r.get_x() + r.get_width() / 2, v + 0.12, f"{v:.1f}%", ha="center", fontsize=8.5)

fig.suptitle("Figure. The demand side of the trust stack: three cross-observatory results.",
             fontsize=9.4, y=1.02, x=0.02, ha="left")
fig.tight_layout(rect=[0, 0, 1, 0.97])
(HERE / "results").mkdir(exist_ok=True)
fig.savefig(HERE / "results/figure-cross-observatory.pdf", bbox_inches="tight")
fig.savefig(HERE / "results/figure-cross-observatory.png", dpi=200, bbox_inches="tight")
print("wrote results/figure-cross-observatory.{pdf,png}")
