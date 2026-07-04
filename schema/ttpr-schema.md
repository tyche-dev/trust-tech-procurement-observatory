# TTPR — Trust-Tech Procurement Record (OCDS-1.1-aligned)

```json
{
  "name": "Trust-Tech Procurement Record (TTPR) — OCDS-aligned unified record",
  "base": "OCDS 1.1 release object (conforms to https://standard.open-contracting.org/1.1/en/release-schema.json). Native-OCDS sources (UK Contracts Finder, UK FTS) map 1:1; non-OCDS sources (TED, USAspending, FPDS, Ireland CKAN) are transformed into OCDS releases at ingest.",
  "core_ocds_fields": {
    "ocid": "stable per-process id, prefixed per source (e.g. 'ttpr-ted-', 'ttpr-usa-', 'ttpr-ukcf-')",
    "id": "release id",
    "date": "release/publication date (NEVER future-dated; drop record if date > harvest date)",
    "tag": [
      "tender",
      "award",
      "contract"
    ],
    "buyer": {
      "name": "",
      "id": ""
    },
    "tender": {
      "title": "",
      "description": "",
      "classification": {
        "scheme": "CPV|NAICS|PSC",
        "id": "",
        "description": ""
      },
      "value": {
        "amount": 0,
        "currency": ""
      }
    },
    "awards": [
      {
        "suppliers": [
          {
            "name": ""
          }
        ],
        "value": {
          "amount": 0,
          "currency": ""
        },
        "date": ""
      }
    ]
  },
  "trust_tech_extension_fields": {
    "tt:domain": "enum AI|PQC|PKI|eIDAS one-or-more — assigned by code+keyword rule, with the matched rule recorded",
    "tt:domain_evidence": "the exact CPV/NAICS/PSC code and/or keyword string that triggered the classification (auditable, not a bare label)",
    "tt:source": "TED|UK-ContractsFinder|UK-FTS|USAspending|FPDS|IE-CKAN",
    "tt:source_url": "exact URL/endpoint the record was fetched from",
    "tt:fetched_at": "ISO timestamp of live fetch (immutable)",
    "tt:http_status": "HTTP status observed at fetch (must be 200 to persist)",
    "tt:raw_hash": "sha256 of the raw upstream payload for this record (immutable baseline / tamper-evidence)",
    "tt:licence": "reuse licence of the source feed"
  },
  "provenance_rule": "Every TTPR MUST carry tt:source_url + tt:fetched_at + tt:http_status + tt:raw_hash or it is rejected at write time. A record with no live fetch behind it cannot exist."
}
```
