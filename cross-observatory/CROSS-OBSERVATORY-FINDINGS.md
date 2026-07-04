# The demand side of the trust stack: cross-observatory findings

*2026-07-04. Every number is computed by `link_analysis.py` from real data; sources are
snapshotted read-only with provenance (`sources/PROVENANCE.json`) and linked, never fused
(the "Link, but Never Fuse" discipline). Figure: `results/figure-cross-observatory.pdf`.*

Inputs: procurement observatory (demand, 4,401 records, Zenodo 10.5281/zenodo.21192405) ×
rQSCD remote-QSCD supply census (114 services, 10 EU states) × obscure-ai reviewed incidents
(998 records, 116 jurisdictions).

## RQ-1 — The quantum-trust cliff (procurement × rQSCD). CONFIRMED, strong.
The EU procures the quantum-**vulnerable** trust layer (PKI + eIDAS, 2,846 records) at **56.9×**
the rate of its quantum-**safe** replacement (PQC, 50 records); on the stricter confirmed
post-quantum count (24) the ratio is **118.6×**. In United States federal award value the
public-key-infrastructure to post-quantum ratio is **90.4×** (USD 566.7M vs 6.3M). This
vulnerable base is not hypothetical: the rQSCD census enumerates **114 remote qualified
signature and seal services across 10 member states**, every one of which runs on today's
public-key cryptography and falls under the eIDAS/ETSI migration horizon. **Reading:** the
abstract "quantum-trust cliff" becomes a two-observatory number with a named denominator — the
state is buying the thing that must be replaced at roughly sixty to a hundred times the rate it
buys the replacement. This is the sharpest extension of the flagship paper and its natural paper 2.

## RQ-2 — Trust-supply concentration (procurement × rQSCD). PRELIMINARY (coverage-bound).
Within the remote-QSCD market the supply is extraordinarily concentrated: **Italy holds 78 of
114 services (68%)**, with the remainder split across Austria, Belgium, Czechia, Estonia,
Luxembourg, Poland, Slovakia, Slovenia and Sweden. Digital-identity procurement demand, by
contrast, is distributed across many member states. **Honest caveat:** the rQSCD census is a
narrow slice (remote QSCD only, 10 states), so the naive "trust deserts" list (states with
identity demand but zero census supply, e.g. Germany, France, Spain) is largely a **census-coverage
artifact**, not evidence those states lack qualified trust services. A complete RQ-2 needs the full
eIDAS Trusted List (the `cassandra-trusted-list-observatory` asset), which would turn the
supply-concentration observation into a defensible demand:supply map. Report as a preliminary,
scope-limited result; do not overclaim deserts.

## RQ-3 — Demand and risk are decoupled (procurement × obscure-ai). INTERESTING, hedged.
Across the 21 jurisdictions observable in both datasets, the rank correlation between AI
procurement volume and AI-incident count is **Spearman rho = -0.129**, i.e. essentially no
positive relationship and a faint negative one. Governments do **not** buy AI in proportion to
where incidents concentrate: the heavy procurers here are European (TED depth), while incidents
concentrate in the United States, Russia and China. **Reading:** procurement is *not* currently a
leading indicator of incident exposure at the country level; demand and observed harm are
decoupled. **Honest caveat:** the two observatories have divergent coverage (procurement
EU-weighted; incidents US/global-weighted), so part of the decoupling is a coverage effect. The
result is suggestive of a genuine demand-risk mismatch but should be presented with the coverage
confound stated, and strengthened later by a within-jurisdiction, category-level crosswalk.

## RQ-4 — The assurance gap, generalised (the umbrella result). CONFIRMED.
The state buys the assured/secured version of a technology at a small fraction of the base it
buys. Crypto layer: post-quantum is **1.76%** of the trust base it must protect (confirmed 0.84%).
AI layer: only **3.72%** of AI procurement records mention any assurance term (audit, conformity,
risk/impact assessment, safety, red-team, evaluation, certification, monitoring, bias,
explainability, trustworthiness, governance). **Reading:** across two independent layers of the
stack the assured share sits below 4%, with the crypto layer the starkest under-buy. This is the
comprehensive-overview headline: a systematic under-procurement of assurance relative to capability.

## RQ-5 — AI procurement → register disclosure (coordinate, do NOT duplicate).
The AI-register disclosure gap is your submitted **Shadow Registry Stage-1 RR**
(`papers/shadow-registry-ai-procurement/`). This observatory should *supply the demand-side
numerator* (plausibly-AI procurement with confidence tiers) to that RR, kept linked not merged.

## Composition
- **RQ-1** is paper 2 (reuses the PQC dataset + one built observatory; highest payoff, lowest new cost). Strong enough to lead.
- **RQ-4** is the umbrella / comprehensive-overview headline (can be its own short piece or the synthesis section of a combined article).
- **RQ-3** is a sibling once the coverage confound is addressed (a within-jurisdiction category crosswalk).
- **RQ-2** waits for the full eIDAS Trusted List (`cassandra` asset) before it is submission-strong.
- **RQ-5** feeds the existing RR.

## Method note (the razor)
Country joins here are exact-tier (ISO-2 / normalised name). The confidence-tier record linkage
(exact-ID / strong-name / keyword-plausible / unmatched) with a positive-control set applies at
the record level for the register (RQ-5) and full-TSL (RQ-2) linkages; those are the steps that
must be pre-registered before data collection, consistent with the Shadow Registry protocol.
