# Scripts — licensed MIT (see /LICENSE). Data produced by them is CC-BY-4.0 (see /DATA-LICENSE).
Pipeline: harvest_*.py (one per source) → consolidate.py (dedup) → validate_observatory.py
(anti-fabrication gate) → analyze.py (statistics) → build_site.py (static site) / deposit_zenodo.py.
Dependency-free (stdlib only) except make_figure1.py (matplotlib) and build_site output.
