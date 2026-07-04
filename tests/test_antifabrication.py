"""Tests for the anti-fabrication guarantees — the software's core contribution.

These assert that the validator ACCEPTS a well-formed, provenance-complete record and
REJECTS each fabrication tell (future date, placeholder host, missing provenance, invented
classification code). Run with: python3 -m pytest tests/  (no third-party deps required
beyond pytest itself).
"""
import datetime
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("validate_observatory", ROOT / "scripts/validate_observatory.py")
val = importlib.util.module_from_spec(spec)
spec.loader.exec_module(val)

HASH = "a" * 64  # valid 64-hex sha256 shape


def good_record():
    return {
        "ocid": "ttpr-test-1", "date": "2025-01-15", "tag": ["award"],
        "buyer": {"name": "Test Ministry", "country": "EE"},
        "tender": {"title": "post-quantum cryptography migration study"},
        "tt:domain": ["PQC"], "tt:domain_evidence": "keyword:post-quantum",
        "tt:source": "TED", "tt:source_url": "https://api.example-gov.test/notices",
        "tt:fetched_at": "2026-07-04T10:00:00+00:00", "tt:http_status": 200,
        "tt:raw_hash": HASH, "tt:licence": "EU-PO-reuse",
    }


def errors_for(record):
    errs = []
    val.check_record(record, errs, "fixture.json")
    return errs


def test_good_record_passes():
    # NB: tt:source_url uses a .test TLD, which the validator's placeholder regex does not flag.
    assert errors_for(good_record()) == []


def test_future_date_rejected():
    r = good_record()
    r["date"] = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
    assert any("FUTURE" in e for e in errors_for(r))


def test_future_fetched_at_rejected():
    r = good_record()
    r["tt:fetched_at"] = (datetime.date.today() + datetime.timedelta(days=5)).isoformat() + "T00:00:00+00:00"
    assert any("FUTURE" in e for e in errors_for(r))


def test_missing_hash_rejected():
    r = good_record()
    r["tt:raw_hash"] = ""
    assert any("raw_hash" in e for e in errors_for(r))


def test_non_hex_hash_rejected():
    r = good_record()
    r["tt:raw_hash"] = "not-a-real-hash"
    assert any("raw_hash" in e for e in errors_for(r))


def test_non_200_status_rejected():
    r = good_record()
    r["tt:http_status"] = 404
    assert any("http_status" in e for e in errors_for(r))


def test_missing_source_url_rejected():
    r = good_record()
    r["tt:source_url"] = ""
    assert any("source_url" in e for e in errors_for(r))


def test_placeholder_host_rejected():
    r = good_record()
    r["tt:source_url"] = "https://example.com/notices"
    assert any("placeholder" in e for e in errors_for(r))


def test_invented_code_rejected():
    r = good_record()
    r["tt:domain_evidence"] = "cpv:99999999"  # not in the verified allowlist
    assert any("allowlist" in e for e in errors_for(r))


def test_allowlisted_code_accepted():
    r = good_record()
    r["tt:domain_evidence"] = "cpv:48732000"  # data security software, in the allowlist
    assert errors_for(r) == []
