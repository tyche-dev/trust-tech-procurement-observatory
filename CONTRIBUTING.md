# Contributing

Thanks for your interest. This project harvests public procurement data under a strict
anti-fabrication contract, so contributions are held to that same standard.

## Ground rules
- **No fabricated data, ever.** A record may enter the corpus only through a `harvest_*.py`
  script that received a live HTTP 200 from a source in `sources/source-ledger.tsv`, and it
  must carry all four provenance fields (`tt:source_url`, `tt:fetched_at`, `tt:http_status`,
  `tt:raw_hash`). Never hand-write, edit, or "estimate" a data record.
- **Never weaken the validator to make data pass.** `scripts/validate_observatory.py` is the
  contract. If a real record fails it, fix the harvester, not the validator.

## Adding a source
Add one `scripts/harvest_<source>.py` that fetches the source and emits records with the four
provenance fields; the validator, consolidator and analyser are source-independent. Record the
endpoint (and its reuse licence) in `sources/source-ledger.tsv`.

## Tests
Run `python3 tests/run_tests.py` (no third-party dependencies) before opening a pull request;
CI runs the same suite. New harvesters should not break the anti-fabrication tests.

## Reporting issues
Open a GitHub issue. For a data-quality concern, include the `ocid` and the source URL so it
can be traced to its provenance stamp.

## Conduct
Be civil and constructive. This is public-interest research infrastructure.
