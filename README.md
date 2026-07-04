# The Trust-Tech Procurement Observatory — a provenance-verified dataset of government demand for AI, post-quantum cryptography, PKI and digital identity

**Version:** v0 (build 2026-07-04) · **Author:** Anton Sokolov, Tyche Institute, Tallinn, Estonia
(ORCID 0000-0003-2452-7096) · **Licence:** CC-BY-4.0 · **Live site:** https://procurement.eatf.eu

This deposit is both a reusable dataset and the manuscript draft of a Data Descriptor. Every
numeric figure below is computed by `scripts/analyze.py` from the committed dataset and was
independently re-verified against the raw records; no figure is an estimate.

## Background & Summary

Governments are simultaneously adopting artificial intelligence and re-building the
cryptographic and identity infrastructure that underpins digital trust — public-key
infrastructure (PKI), the migration to post-quantum cryptography (PQC), and eIDAS-style
digital identity. What they *procure* is a leading, public, and under-used signal of that
activity, yet no open dataset tracks trust-technology procurement across domains and
jurisdictions with verifiable provenance.

The Trust-Tech Procurement Observatory is a live, deduplicated corpus of government and
inter-governmental procurement notices and awards tagged to four domains — **AI, PQC, PKI,
eIDAS/digital identity** — harvested from four public sources. This v0 release holds
**4,401 unique records spanning 106 countries**.

By domain: PKI 1,727 records, AI 1,505, eIDAS 1,119, PQC 50. By source: EU TED 3,290,
US USAspending 561, World Bank 547, UK Contracts Finder 3.

**Headline finding — the post-quantum procurement gap.** PQC appears in only **50 of 4,401
records (1.14%)** — 3.03% of the US slice (17/561), 1.0% of the EU slice (33/3,290), and 0%
of the World Bank development-finance slice (0/547). This is set against a policy context
(reported here as context, not as a dataset measurement) in which NIST finalized the ML-KEM,
ML-DSA and SLH-DSA standards (FIPS 203/204/205) in August 2024 and the US NSA CNSA 2.0 suite
sets migration deadlines across 2030–2033. Where US dollar values are available, PQC-tagged
federal spend totals USD 6,269,846 against USD 566,664,128 for PKI and USD 154,331,410 for
AI. Mandates exist; the procurement signal is, so far, almost invisible.

## Methods

**Anti-fabrication by construction.** The corpus's predecessor project was compromised by an
automated pipeline that fabricated sources. This dataset is built so that fabrication is
structurally impossible:

1. **Live-fetch-or-drop.** A record exists only if a deterministic harvest script received an
   HTTP 200 from a source listed in `source-ledger.tsv` during that run. There is no manual
   insertion path and no language model in the harvest loop.
2. **Provenance-required.** Every record carries `tt:source_url`, `tt:fetched_at`,
   `tt:http_status` (must be 200), and `tt:raw_hash` (sha256 of the raw upstream payload). A
   record missing any of these is rejected at write time by `scripts/validate_observatory.py`,
   which also hard-fails on future dates, placeholder hosts, and classification codes outside a
   verified allowlist.
3. **Deterministic transformation.** Native-OCDS sources (UK) map one-to-one; non-OCDS sources
   (TED, USAspending, World Bank) are transformed to a common OCDS-1.1-aligned record (the
   TTPR, see `methods/ttpr-schema.md`). `scripts/consolidate.py` deduplicates across harvest
   runs by `ocid`. `scripts/analyze.py` computes every reported statistic.

**Domain selection.** For keyword-dominant domains the harvesters query source full-text
indices directly (e.g. TED `FT ~ "post-quantum"`); where a coding system helps, only
live-verified CPV/NAICS/PSC codes are used (see `methods/domain-selection.md`).

**Sources & licences.** EU TED (v3 full-text API, EU Publications Office reuse); US
USAspending.gov (public domain); UK Contracts Finder / Find-a-Tender (OGL v3.0); World Bank
procurement notices (open). Per-record licence recorded in `tt:licence`; this aggregate is
released CC-BY-4.0 with per-source attribution preserved.

## Data Records

- `data/dataset.json` — the consolidated corpus: an OCDS-1.1 release package, 4,401 unique
  releases, each with the `tt:` provenance extension.
- `data/analysis.json` — all computed statistics (by domain, region, country, year, source;
  the PQC-gap metric; US value totals; top buyers).
- `data/stats.json` — coverage summary (unique records, countries, region × domain matrix).
- `data/findings-2026-07-04.{json,md}` — the verified findings narrative.
- `source-ledger.tsv` — the eleven verified source endpoints (and one dropped).
- `scripts/` — the full harvest / validate / consolidate / analyze pipeline.
- `methods/` — schema, domain-selection strategy, phase plan.

## Technical Validation

`scripts/validate_observatory.py` passes on this release: all provenance fields present, no
future dates, no placeholder hosts, all classification codes in the verified allowlist. The
findings numbers were drafted and then adversarially re-verified: each figure was re-computed
directly from `data/dataset.json` and reproduced exactly.

## Usage Notes & Limitations

Coverage is a **curated demand-signal sample, not a population census.** The EU (TED) lane is
the deepest and near-complete for above-threshold tenders, which is why EU member states
dominate the country ranking (Germany 886 records, Poland 324, France 267). The US and UK
lanes are keyword-sparse and undercount. The World Bank lane reflects development-finance
procurement; its 0% PQC share may reflect that PQC is not yet a tracked category rather than
true absence. Dollar values exist only for the US award lane. Domain tags are not, in
principle, mutually exclusive. Records cluster recently (2022: 376; 2023: 344; 2024: 496;
2025: 1,191; 2026: 886 year-to-date), partly a coverage-window effect. Cross-region
comparisons are comparisons of *visible* procurement, not of total national spend.

## Code Availability

All harvest, validation, consolidation and analysis code is in `scripts/` and re-runnable
with a standard Python 3 install (no third-party dependencies). The live observatory is at
https://procurement.eatf.eu.
