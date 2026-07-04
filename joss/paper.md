---
title: 'A provenance-verified, anti-fabrication pipeline for cross-domain public procurement observatories'
tags:
  - Python
  - open contracting
  - public procurement
  - data provenance
  - reproducibility
  - Open Contracting Data Standard
authors:
  - name: Anton Sokolov
    orcid: 0000-0003-2452-7096
    affiliation: 1
affiliations:
  - name: Tyche Institute, Tallinn, Estonia
    index: 1
date: 4 July 2026
bibliography: paper.bib
---

# Summary

This software harvests public-sector procurement notices and awards from national and
inter-governmental sources, tags each record to one or more technology domains, and
assembles them into a single, deduplicated, Open Contracting Data Standard-aligned corpus.
Its distinguishing feature is that it is built so that fabricated records cannot enter the
dataset. Every record is produced by a deterministic harvest step that must receive a live
successful response from a listed source, and every record carries an immutable provenance
stamp: the source endpoint, the fetch timestamp, the observed response status, and a
SHA-256 hash of the raw upstream payload. A validator rejects, at write time, any record
that lacks a provenance field, that carries a future date, that names a placeholder host,
or that carries a classification code outside a verified allowlist. A consolidation step
deduplicates records across harvest runs, and an analysis step computes every summary
statistic directly from the committed records, so that no reported figure can be asserted
without the records behind it. The pipeline is pure Python with no third-party runtime
dependencies, and it drives a live public observatory of trust-technology procurement.

# Statement of need

Public procurement is one of the most complete administrative records a state produces, and
in several jurisdictions it is published in structured, machine-readable form. It is
therefore an attractive instrument for research on state demand, on technology adoption, and
on the gap between policy mandates and purchasing behaviour. Two obstacles have limited its
use. First, the data is fragmented across national systems and coding schemes, so a
cross-domain, cross-jurisdiction view requires harvesting and normalising several
heterogeneous sources. Second, and more corrosively, researchers who assemble such views
often depend on aggregators or ad-hoc pipelines whose provenance is opaque, which makes any
finding, and especially any finding that rests on an absence, difficult to trust.

This project was written after a predecessor pipeline was compromised by an automated
process that fabricated sources, inventing registries and back-dating verification. The
lesson drawn was that trust in a procurement corpus should not rest on the assumption that
collection was honest, but on a construction in which dishonest or fabricated records cannot
enter. The software meets that need with a small, auditable, dependency-free pipeline whose
provenance guarantees are enforced mechanically rather than by convention. It is aimed at
researchers, oversight bodies, and civic-technology practitioners who need a procurement
corpus they can defend, and at maintainers of open-contracting infrastructure who want a
reusable pattern for provenance-required ingestion.

The software currently harvests the European Union Tenders Electronic Daily API, United
States USAspending.gov award data, United Kingdom Contracts Finder and Find a Tender OCDS
feeds, and World Bank procurement notices, and it tags records to four trust-technology
domains (artificial intelligence, post-quantum cryptography, public-key infrastructure, and
eIDAS or digital identity). Adding a source requires only a new harvest module that emits
the common record with its provenance fields; the validator, consolidator and analyser are
source-independent. The corpus it produces is published on Zenodo under a Creative Commons
Attribution licence [@dataset], and the live observatory is documented in an accompanying
data descriptor.

# Design

The pipeline is organised as independent, composable stages. Harvest modules
(`harvest_*.py`) each fetch one source, transform its response into the common record, and
attach the four provenance fields. A record with no live successful fetch behind it is never
written. `consolidate.py` merges all harvested release packages and deduplicates by stable
identifier, keeping the most recent fetch. `validate_observatory.py` enforces the provenance
contract and the anti-fabrication invariants and exits non-zero on any violation, which makes
it usable as a continuous-integration gate. `analyze.py` computes the summary statistics used
by downstream reporting and the static-site builder, `build_site.py`. Because the analysis is
deterministic and reads only committed records, any published figure can be reproduced by
re-running the analyser, and the reporting layer cannot introduce a number that the data does
not support.

# Acknowledgements

The source data is provided by the European Union Publications Office (Tenders Electronic
Daily), the United States government (USAspending.gov), the United Kingdom government
(Contracts Finder and Find a Tender, Open Government Licence v3.0), and the World Bank.

# References
