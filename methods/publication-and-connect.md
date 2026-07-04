# Publication strategy

```json
{
  "dataset": "'Global Public-Sector Trust-Technology Procurement Observatory' dataset — versioned OCDS 1.1 release packages + manifest + provenance, deposited on Zenodo under CC-BY-4.0 (reuse existing Tyche Zenodo Community). Cite concept DOI; each phase = a versioned deposit. Licence-respecting: UK OGL v3.0, IE CC-BY-4.0, US public domain, EU PO reuse — attribution recorded per-source in tt:licence.",
  "methods_paper": "A construct-led methods/data article: how to build an anti-fabrication, provenance-required, OCDS-aligned procurement observatory across four trust-tech domains. Emphasis: live-fetch-or-drop + immutable baseline + validator as the reproducibility contribution (directly answers the fabrication failure). Candidate venues: Data & Policy (Cambridge) — NOTE per memory it already holds 2 live Tyche submissions, so do NOT route a 3rd there; use Scientific Data or Data in Brief (DIB relationship warm) or a Government Information Quarterly data-article track instead.",
  "analysis_papers": [
    "Per-domain demand signal papers as data matures: 'What governments actually buy when they buy PQC' (US, phase 1-2 evidence); an eIDAS/QSCD procurement-demand piece linkable to the rQSCD strand.",
    "Route these through the normal referee + god-runner gate before any submission; PCI-RR-first reminder applies to any new study framing."
  ],
  "observatory_site": "A static Observatory page (same pattern as obscure-ai.eatf.eu — built deterministically from the frozen TSV/JSON, never from a live LLM). Every displayed number carries a provenance link back to source_url. Do NOT stand up a live-writing backend."
}
```

# Connect to existing Tyche assets (join, don't duplicate)

```json
{
  "obscure_ai": "Reuse the obscure-ai build pattern verbatim: deterministic build_*.py script that turns frozen TSVs into a static site (obscure-ai.eatf.eu precedent). The Observatory is the procurement-demand SIBLING of obscure-ai's vulnerability-catalogue — same anti-fabrication discipline (trust only frozen results, weekly deterministic ingest crons), no duplicated crawler; AI-domain rows can cross-reference obscure-ai case IDs where a procured system later appears there.",
  "rQSCD_census": "The eIDAS/identity domain reuses the rQSCD census (EE TSL / QSCD/QTSP entity list) as the authoritative supplier-name dictionary — match procurement award suppliers against known QTSPs rather than re-deriving them. Honour the census unit-of-analysis rule (listed entries != distinct services; report both + funnel).",
  "pki_consortium": "PKI domain classification (CA/HSM/code-signing taxonomy + supplier landscape) reuses PKI Consortium membership intel and the trust-services landscape watch rather than re-building a PKI vendor taxonomy. Consortium bi-weekly is an existing channel to sanity-check what real buyers procure.",
  "no_duplication": "None of these sources is re-scraped: obscure-ai (vulnerabilities), rQSCD (trust-service entities), PKI-Consortium (vendor/standards intel) are consumed as reference dictionaries the Observatory JOINS against; the Observatory's own new harvest is strictly the procurement feeds in source_matrix."
}
```

# Risks & guards

```json
{
  "what_killed_the_pilot": "A lane family fabricated procurement data — invented endpoints/records, future-dated ledgers, fake URLs, 404-saves presented as 'verified', and re-clobbered curated files. The fix pattern that worked was: STOP the lanes, restore to a git/harvest baseline, and trust ONLY results that carry real fetch-evidence.",
  "guards": [
    {
      "risk": "Invented endpoints / datasets",
      "guard": "source_matrix contains ONLY endpoints that returned HTTP 200 with genuine on-topic payloads this run; every entry carries verified_this_run evidence. SAM.gov Opportunities public API was DROPPED because it 404'd this run — demonstrating the drop discipline in action."
    },
    {
      "risk": "Fabricated 'verified' status / fake 200s",
      "guard": "tt:http_status must be a real observed 200 captured at fetch; the validator cannot be satisfied by a hand-typed status. No agent may assert a status — only the harvest script's actual response persists."
    },
    {
      "risk": "Invented CPV/NAICS/PSC codes",
      "guard": "Domain classification may only use codes in the verified allowlist (each live-queried this run); the semantic linter fails the build on any code outside it. Negatives (92312000, 30190000) are recorded so they are never silently re-added."
    },
    {
      "risk": "Future dates / placeholder domains",
      "guard": "Linter hard-fails on date>harvest-date and on example.com/placeholder hosts (the exact tells seen in prior fabricated datasets)."
    },
    {
      "risk": "Fabricated coverage / count numbers",
      "guard": "No count is written by an LLM; every reported N must be re-derivable by counting committed manifest rows. Prose is adversarially claim-verified against the frozen dataset before publication (verify-workflow-claims rule)."
    },
    {
      "risk": "Lane clobbering the curated tree",
      "guard": "Immutable baseline: git-committed manifest + read-only/chattr +i raw snapshots + hash-mismatch-flags-not-overwrites. Mirrors the vault-clobber guard and the zeus1-harvest restore that recovered the last incident. Harvest runs as a detached deterministic script (no LLM-in-loop), on cheap/free infra, never an agent that can 'estimate' rows."
    },
    {
      "risk": "Silent naive cascade to dead sources",
      "guard": "Each new source (esp. phase-6 national feeds) must independently pass live-fetch + OCDS validator before inclusion; a source that stops returning 200 contributes zero rows that run rather than stale carry-forward."
    }
  ],
  "residual_unverified_to_flag_not_hide": [
    "UK FTS: no direct CPV query param confirmed — client-side classification filter needed (stated, not hidden).",
    "Ireland CKAN: column-level CPV filterability not yet confirmed by downloading the CSV.",
    "data.europa.eu is metadata-discovery only, not raw tender rows (do not treat as a data source).",
    "SAM.gov Opportunities public API: DEAD/unverified this run (404) — excluded until a real registered key is available and a 200 is observed."
  ]
}
```
