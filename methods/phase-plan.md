# Phase plan

```json
[
  {
    "phase": 1,
    "cell": "region=US x domain=PQC x source=USAspending.gov spending_by_award API",
    "why_this_cell": "Single highest-signal, lowest-risk cell: no auth, POST JSON, and the keyword='post-quantum cryptography' query returns GENUINE federal awards with rich descriptions ('harvest now decrypt later') — verified live twice (scout + this run). PQC is keyword-dominant so it needs no fragile code mapping, and US awards are public-domain (cleanest licence). It proves the whole method — live-fetch, provenance, OCDS transform, validator, immutable baseline — on the least ambiguous data.",
    "first_steps": {
      "api": "POST https://api.usaspending.gov/api/v2/search/spending_by_award/",
      "query": "{\"filters\":{\"award_type_codes\":[\"A\",\"B\",\"C\",\"D\"],\"keywords\":[\"post-quantum cryptography\"]},\"fields\":[\"Award ID\",\"Recipient Name\",\"Award Amount\",\"Description\",\"Action Date\",\"Awarding Agency\"],\"limit\":100}",
      "then": "Paginate; for each award: capture tt:fetched_at + tt:http_status=200 + sha256(raw)=tt:raw_hash; transform to OCDS 1.1 release with tt:domain=PQC and tt:domain_evidence='keyword:post-quantum cryptography'; run libcoveocds to assert conformance.",
      "v0_output": "A git-committed pqc-us-v0 dataset: OCDS 1.1 release package (N real awards) + a manifest.csv of {ocid, recipient, amount, action_date, tt:raw_hash} + a one-line provenance line per row. Baseline frozen (read-only + committed). Every number in any writeup must be re-countable from manifest.csv."
    }
  },
  {
    "phase": 2,
    "cell": "region=US x domain=PKI x source=FPDS-NG ATOM feed",
    "deliverable": "Add FPDS PSC D-family harvest with PKI/HSM/certificate keyword refinement; second US source cross-validates USAspending on overlapping awards (dedup by PIID). Extends TTPR to a second non-OCDS transform path."
  },
  {
    "phase": 3,
    "cell": "region=UK x domain=AI+PQC+PKI+eIDAS x source=Contracts Finder OCDS Search API",
    "deliverable": "First native-OCDS ingest (1:1 map, no transform risk) using confirmed cpv_codes filter (72000000/48000000/79417000/48732000) + keyword layer per domain. Proves cross-domain coverage on the best-verified endpoint. Adds UK FTS date-window harvest for above-threshold notices."
  },
  {
    "phase": 4,
    "cell": "region=EU x domain=all-4 x source=TED API v3",
    "deliverable": "EU-27 coverage via classification-cpv queries per domain; transform eForms/JSON to TTPR. Highest-volume source — run detached with backoff/cap. Reconcile against UK to measure cross-border overlap."
  },
  {
    "phase": 5,
    "cell": "region=Ireland x domain=all-4 x source=data.gov.ie CKAN bulk (+ EU discovery via data.europa.eu)",
    "deliverable": "Add CC-BY-4.0 Ireland historical bulk (2013–2026) for time-series depth; use data.europa.eu Dataset Hub to enumerate additional national OCDS publishers from the OCP registry for phase-6 expansion candidates."
  },
  {
    "phase": 6,
    "cell": "region=Global x domain=all-4 x source=OCP registry-listed national OCDS feeds",
    "deliverable": "Onboard next verified national OCDS publishers (each must pass a live-fetch + validator gate before inclusion). Publish the consolidated cross-region Observatory dataset + methods paper."
  }
]
```

## Pipeline controls

```json
{
  "live_fetch_or_drop": "A record is only written if the harvest run produced an HTTP 200 from a source_matrix endpoint THIS run. No cached-forward, no 'known-good from last time', no manual insertion. If an endpoint returns non-200/NXDOMAIN, that source is marked DEAD for the run and contributes zero rows (never synthetic fill). Enforced example: SAM.gov Opportunities public API returned 404 this run (no key AND fake key) — it is DROPPED, not backfilled.",
  "provenance_required": "Write-time validator rejects any TTPR missing tt:source_url, tt:fetched_at, tt:http_status==200, or tt:raw_hash. No provenance = no row. This is the single control that structurally prevents the fabrication that killed the pilot.",
  "immutable_baseline": "On first successful harvest, freeze a baseline: git-committed manifest of {ocid, tt:raw_hash, tt:fetched_at} per record + chattr +i / read-only snapshot of raw payloads. Later runs may ADD rows or supersede with a new dated release, but MUST NOT silently rewrite a baselined raw_hash. Any hash mismatch on re-harvest = flagged, not overwritten (mirrors the vault-clobber guard + zeus1-harvest restore pattern).",
  "validator": "Two-stage: (1) STRUCTURAL — run libcoveocds / ocdskit (both live on PyPI this run) to assert OCDS 1.1 conformance on every transformed release; (2) SEMANTIC anti-fabrication linter that fails the build on: future dates, placeholder domains (example.com), invented CPV/NAICS/PSC codes not in the verified code allowlist, any record whose tt:domain_evidence code was not itself HTTP-200-queried this run, and any coverage/count number not derivable by re-counting the committed rows.",
  "no_llm_in_harvest_loop": "Harvest is a detached deterministic script (cache + backoff + cap), never an agent-in-loop that can 'summarize' or 'estimate' rows. LLM use is confined to downstream prose/figure drafting, which is then adversarially claim-verified against the frozen dataset before any publication."
}
```
