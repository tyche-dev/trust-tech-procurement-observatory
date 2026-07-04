# Domain selection — verified codes + keywords (live-queried 2026-07-02)

> Every code below returned real notices/awards this run. Codes tried and found NOT relevant are in `negatives_do_not_reuse` — never re-add them.

```json
{
  "principle": "Two-layer selection: (1) broad code net at harvest time using ONLY live-verified CPV/NAICS/PSC codes; (2) keyword refinement to separate the four domains from generic IT. All codes below were live-queried this run and returned real notices/awards — no code is asserted without an HTTP-200 query behind it. Codes tried and found NOT domain-relevant are recorded as negatives so they are not reused.",
  "AI": {
    "eu_uk_cpv": [
      "72000000-5 IT services: consulting, software development",
      "48000000-8 Software package and information systems"
    ],
    "us_naics": [
      "541512 Computer Systems Design Services"
    ],
    "keyword_refine": [
      "artificial intelligence",
      "machine learning",
      "automated decision",
      "algorithm",
      "predictive model",
      "large language model",
      "facial recognition"
    ],
    "note": "CPV has no AI-specific code; AI contracts hide inside 72/48. Keyword layer is mandatory to isolate AI from generic IT. Do NOT claim a CPV 'AI code' exists — none verified."
  },
  "PQC": {
    "eu_uk_cpv": [
      "79417000-0 Security consultancy services",
      "48732000-8 Data security software packages"
    ],
    "us_naics": [
      "541512 Computer Systems Design Services (+ keyword)"
    ],
    "keyword_refine": [
      "post-quantum",
      "post quantum cryptography",
      "quantum-safe",
      "quantum resistant",
      "crypto-agility",
      "FIPS 203",
      "FIPS 204",
      "FIPS 205",
      "ML-KEM",
      "ML-DSA",
      "CNSA 2.0",
      "harvest now decrypt later"
    ],
    "note": "PQC is keyword-dominant: live USAspending keyword search returned genuine DoD PQC awards. FIPS 203/204/205 are the real published NIST PQC standard numbers; use as high-precision keywords, not as procurement codes."
  },
  "PKI": {
    "eu_uk_cpv": [
      "79417000-0 Security consultancy services",
      "48732000-8 Data security software packages",
      "72000000-5 IT services (broad net)"
    ],
    "us_psc": [
      "D-family PSC (IT/telecom services) via FPDS PRODUCT_OR_SERVICE_CODE"
    ],
    "keyword_refine": [
      "public key infrastructure",
      "PKI",
      "certificate authority",
      "HSM",
      "hardware security module",
      "key management",
      "code signing",
      "X.509",
      "certificate lifecycle"
    ],
    "note": "Military-crypto adjacency codes 35700000-1 / 35711000-1 verified live on TED but treat as ADJACENT (noisy) — keyword-gate before counting."
  },
  "eIDAS_identity": {
    "eu_uk_cpv": [
      "72000000-5 IT services",
      "48000000-8 Software packages",
      "79417000-0 Security consultancy"
    ],
    "keyword_refine": [
      "eIDAS",
      "digital identity",
      "digital wallet",
      "EUDI wallet",
      "QSCD",
      "QTSP",
      "qualified trust service",
      "eID",
      "electronic signature",
      "identity verification"
    ],
    "note": "No eIDAS-specific procurement code; keyword-dominant. Cross-link to Tyche rQSCD census for QSCD/QTSP entity names."
  },
  "negatives_do_not_reuse": [
    "92312000-1 Artistic services — verified live but NOT security/domain-relevant (scout's initial guess wrong; recorded so it is never re-added)",
    "30190000-7 — returns real notices but exact label unconfirmed and not domain-relevant (office/IT equipment cluster); do not cite a label"
  ]
}
```
