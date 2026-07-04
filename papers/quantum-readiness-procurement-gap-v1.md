# The Quantum-Readiness Procurement Gap: government demand for post-quantum cryptography measured against artificial intelligence, public-key infrastructure and digital identity

**Anton Sokolov**
Tyche Institute, Tallinn, Estonia · ORCID 0000-0003-2452-7096 · anton.sokolov@tyche.institute

*Draft v1, 2026-07-04. Dataset: Zenodo 10.5281/zenodo.21192405 (CC-BY-4.0). Observatory: https://procurement.eatf.eu*

## Abstract

Governments have finalized the cryptographic standards for the post-quantum transition and have set formal deadlines for migrating away from quantum-vulnerable cryptography. Whether that policy commitment is yet visible in what governments buy is an open, and measurable, question. We assemble a live, provenance-verified corpus of 4,401 public-sector procurement records across four trust-technology domains (artificial intelligence, post-quantum cryptography, public-key infrastructure, and eIDAS or digital identity), drawn from four public procurement sources spanning 106 countries, and use it to measure the demand signal for post-quantum cryptography against the demand for adjacent trust technologies. Post-quantum cryptography accounts for 50 of 4,401 records, or 1.14 percent of the corpus, against 1,727 records for public-key infrastructure and 1,505 for artificial intelligence. In United States federal award data, where monetary values are available, post-quantum cryptography accounts for USD 6.3 million against USD 566.7 million for public-key infrastructure. The gap holds across every region we measure and is widest in World Bank-financed procurement, where we observe no post-quantum records. We interpret this as a measurable distance between a maturing mandate and an as-yet-faint procurement signal, discuss the competing explanations, and argue that the procurement record is an under-used and independently verifiable instrument for tracking the readiness of the state for the post-quantum transition. The corpus is built so that fabrication is structurally impossible, and every figure reported here is recomputable from the published data.

## 1. Introduction

A cryptographically relevant quantum computer would break the public-key cryptography that protects most digital communication and stored records today. The response of the standards community has moved from research to instruction. In August 2024 the United States National Institute of Standards and Technology finalized its first three post-quantum cryptographic standards, ML-KEM, ML-DSA and SLH-DSA, published as FIPS 203, 204 and 205. The United States National Security Agency, through its Commercial National Security Algorithm Suite 2.0, has set migration deadlines that run from 2030 to 2033 for national security systems, and executive guidance has directed federal agencies to inventory and prioritize their cryptographic migration. The European Union, through its coordinated post-quantum roadmap and the work of national cybersecurity agencies, has issued parallel guidance. The threat model that motivates this urgency, often described as "harvest now, decrypt later," assumes that an adversary can record encrypted traffic today and decrypt it once a quantum computer becomes available, which makes the migration deadline earlier in practice than the arrival of the machine.

Policy of this kind is meant to change behaviour, and one of the most concrete behaviours a government exhibits is what it buys. Procurement notices and contract awards are public in most jurisdictions, are timestamped, and name the buyer and the object of purchase. They are, in principle, a leading indicator of whether a mandate has begun to move money. Yet the procurement record is rarely read this way, in part because it is fragmented across national systems and coding schemes, and in part because assembling a cross-domain, cross-jurisdiction view of it has historically required trusting aggregators whose provenance is opaque.

We take the procurement record seriously as a measurement instrument. This article makes three contributions. First, we assemble and publish a live, provenance-verified corpus of trust-technology procurement across four domains and 106 countries, built so that a record cannot exist without a verifiable live source. Second, we use that corpus to measure the demand signal for post-quantum cryptography and to place it in the context of demand for the adjacent trust technologies that governments are buying at the same time. Third, we report a specific finding, which we call the quantum-readiness procurement gap: post-quantum cryptography is, so far, almost absent from the procurement record, and the absence is consistent across every region and value measure we examine, against a backdrop of substantial and growing procurement of the very infrastructure that the post-quantum transition is meant to protect.

We are careful about what this measures. The corpus records demand signals, meaning what buyers advertised or awarded, and it is a curated coverage sample rather than a census of all government procurement. The finding is descriptive. We do not claim to measure compliance, intent, or the true rate of cryptographic migration, some of which happens through channels that never appear as a distinctly labelled procurement. We claim only that the visible, nameable, purchasable demand for post-quantum cryptography is, at the time of measurement, very small relative to the mandate and relative to adjacent trust-technology demand, and that this is worth measuring and watching.

## 2. Background

### 2.1 Standards and mandates

The post-quantum transition is unusual among cryptographic migrations in that its schedule is set by policy rather than by the discovery of a break in a deployed algorithm. The three finalized National Institute of Standards and Technology standards give implementers concrete targets. The Commercial National Security Algorithm Suite 2.0 and associated United States executive guidance convert those targets into deadlines and inventory obligations for national security and federal systems. Comparable coordination is under way in the European Union and in individual member states through national cybersecurity agencies. The practical consequence is that, for a large class of public buyers, quantum-safe cryptography moved from optional to expected over the period our corpus covers.

### 2.2 Procurement as a signal, and why it is hard to read

Public procurement is one of the most complete administrative records a state produces, and in the European Union above-threshold tenders are published centrally and in structured form. The signal is nonetheless hard to read across domains and borders for three reasons. Coding systems differ, so a purchase of cryptographic services carries a different classification code in the European Union than a comparable purchase in the United States. Trust-technology purchases hide inside broad information-technology categories rather than carrying a dedicated code, so a keyword layer is required to separate, for instance, an artificial-intelligence contract from a generic software contract. And the completeness of the underlying feeds varies, so a naive cross-country count reflects the depth of each feed as much as the behaviour of each government. We address the first two problems with a full-text and code-based selection strategy documented with the corpus, and we address the third by reporting coverage caveats alongside every cross-region comparison rather than presenting raw counts as if they were a census.

### 2.3 Trustworthy measurement

The corpus that supports this article is the successor to an earlier project that was compromised when an automated pipeline fabricated sources, inventing registries and back-dating verification. That experience shaped the present design. Rather than ask readers to trust that the data was collected honestly, we built the collection so that a fabricated record cannot enter it. We describe the mechanism in Section 3 because, for a finding that rests on an absence, the credibility of the measurement is as important as the measurement itself. An absence is only informative if the reader can rule out that it is an artifact of a broken or dishonest pipeline.

## 3. Data and methods

### 3.1 Sources and scope

The corpus draws on four public procurement sources. From the European Union we harvest Tenders Electronic Daily, the central publication venue for above-threshold notices across the member states, through its version 3 application programming interface. From the United States we harvest federal award data from USAspending.gov. From the United Kingdom we harvest Contracts Finder and the Find a Tender Service. For the wider world we harvest World Bank procurement notices, which cover procurement financed by the Bank across a large set of borrower countries. Each source is public and carries an open or reuse-permitting licence, recorded per record and preserved in the aggregate release under a Creative Commons Attribution licence.

We tag each record to one or more of four domains: artificial intelligence, post-quantum cryptography, public-key infrastructure, and eIDAS or digital identity. For domains where a coding system helps, we use only classification codes that we verified return real notices. For domains that are keyword-dominant, including post-quantum cryptography, we query source full-text indices directly for domain terms, which allows us to find relevant notices regardless of the language of the notice. The selection strategy is documented and published with the corpus.

### 3.2 Anti-fabrication by construction

A record enters the corpus only if a deterministic harvest script received a live successful response from a listed source during the harvest run. There is no manual insertion path, and no language model participates in the harvest loop. Every record carries four provenance fields: the exact source endpoint, the fetch timestamp, the observed response status, and a SHA-256 hash of the raw upstream payload from which the record was derived. A validator rejects, at write time, any record that lacks a provenance field, that carries a future date, that names a placeholder host, or that carries a classification code outside the verified set. Records are deduplicated across harvest runs by their stable identifier. Every statistic reported in this article is computed by a single analysis script from the committed records, so that any reported figure can be recomputed, and no figure can be asserted without the records behind it. The full pipeline is open and free of third-party dependencies.

This construction matters for the interpretation of our central finding. Because a record cannot exist without a verifiable live source, the small post-quantum count is not the residue of a filter that silently discarded post-quantum records, nor the product of a source we failed to reach. It is what the four listed sources returned.

### 3.3 What the corpus measures, and what it does not

The corpus measures the visible demand signal, meaning notices and awards that a buyer published or made, tagged to a trust-technology domain. It is a curated coverage sample. The European Union source is the deepest and is close to complete for above-threshold tenders, which is why European member states dominate the country ranking. The United States and United Kingdom sources are keyword-sparse in our current build and undercount relative to the European Union. The World Bank source reflects development-finance procurement rather than general government procurement. Monetary values are available only for the United States award source. These properties bound the claims we make. We report within-source and within-region shares, we compare like with like, and we treat every cross-region comparison as a comparison of visible procurement rather than of total national spend.

## 4. Results

### 4.1 The four-domain demand picture

The corpus holds 4,401 unique records spanning 106 countries. Table 1 gives the distribution across domains and regions. Public-key infrastructure is the largest domain with 1,727 records, ahead of artificial intelligence with 1,505 and eIDAS or digital identity with 1,119. Post-quantum cryptography is the smallest by a wide margin, with 50 records. Grouping the three cryptography-and-identity domains together, security and identity procurement accounts for 2,896 records against 1,505 for artificial intelligence, so the trust-infrastructure domains together outweigh artificial intelligence in the visible record by close to two to one.

**Table 1. Records by region and domain.**

| Region | AI | PKI | PQC | eIDAS | Total |
|:-------|---:|----:|----:|------:|------:|
| EU | 1,200 | 1,094 | 33 | 963 | 3,290 |
| US | 73 | 471 | 17 | 0 | 561 |
| Global (World Bank) | 230 | 162 | 0 | 155 | 547 |
| UK | 2 | 0 | 0 | 1 | 3 |
| Total | 1,505 | 1,727 | 50 | 1,119 | 4,401 |

The regional totals are shaped by source depth, as Section 3.3 notes, and the European Union figure reflects the near-completeness of the Tenders Electronic Daily feed rather than a claim that European governments buy the most trust technology in absolute terms. The comparison we draw below is within region wherever possible, which neutralizes that source-depth effect.

### 4.2 The quantum-readiness procurement gap

Post-quantum cryptography accounts for 50 of 4,401 records, or 1.14 percent of the corpus. The share is small in every region we measure and does not depend on the source-depth caveat, because it is a within-region ratio. In United States federal data, post-quantum cryptography is 17 of 561 records, or 3.03 percent. In European Union data it is 33 of 3,290 records, or 1.0 percent. In World Bank-financed procurement it is 0 of 547 records. The United States share, though the highest of the three, still places post-quantum cryptography an order of magnitude below public-key infrastructure within the same source and jurisdiction.

The monetary comparison, available for the United States award source, is starker than the record count. Post-quantum cryptography accounts for USD 6.3 million of tagged federal award value, against USD 566.7 million for public-key infrastructure and USD 154.3 million for artificial intelligence. Public-key infrastructure, the incumbent cryptographic infrastructure that the post-quantum transition is meant to succeed, attracts roughly ninety times the award value of its designated successor in the same records.

The shape of the gap is therefore consistent across three independent cuts of the data: it appears in the overall share, it appears within each region as a within-region ratio, and it appears in monetary value where value is measured. A finding that survives these three cuts is unlikely to be an artifact of any single measurement choice.

### 4.3 Who is buying post-quantum cryptography

The 50 post-quantum records are not evenly distributed, and the early movers are informative. In the European Union, the most frequent post-quantum buyer is Poland's Centralny Osrodek Informatyki, the state information-technology centre, followed by the Netherlands Enterprise Agency and the Polish National Centre for Research and Development, with further records from a German research university, a Croatian public institute, and the European Cybersecurity Competence Centre. In United States data the Department of Defense is the most frequent post-quantum buyer, consistent with the fact that national security systems carry the earliest migration deadlines, and one of its awards names the "harvest now, decrypt later" threat explicitly. The pattern is one of a small set of technically sophisticated, mandate-exposed public bodies moving first, rather than a broad base of buyers.

By contrast, the most frequent buyers in the large domains are broad and operational. In public-key infrastructure they are interior ministries and defence, homeland-security and state departments. In artificial intelligence they include a German statutory health insurer, defence, an agricultural university, and the European Commission's communications-technology directorate. The contrast between a narrow, specialist post-quantum buyer base and a broad, operational buyer base for the incumbent domains is itself part of the finding.

### 4.4 Trajectory

The corpus clusters in recent years, with 376 records dated 2022, 344 in 2023, 496 in 2024, 1,191 in 2025, and 886 in the year-to-date portion of 2026. We caution that yearly totals are shaped by the publication windows of the sources and by our collection window, so the rise should be read as a coverage-and-activity signal rather than as a precise growth rate. Within that caveat, the record is consistent with rising overall trust-technology procurement over the period in which the post-quantum mandate matured, which makes the flatness of the post-quantum signal against that rising baseline the more notable.

## 5. Discussion

### 5.1 Competing explanations for the gap

A near-absence in a procurement record admits several explanations, and honest measurement means naming them.

The first is a genuine lag. Mandates with deadlines in 2030 to 2033 may simply not have moved procurement money yet, with buyers still in the inventory-and-planning phase that the executive guidance prescribes before purchasing. Under this reading the gap is real and the procurement signal is an early and truthful indicator that migration has not yet reached the buying stage at scale.

The second is procurement invisibility. Post-quantum migration may be happening inside contracts that are not labelled as post-quantum, for example as a routine feature of a broader information-security services contract, a software update, or a hardware refresh, in which case the demand exists but does not surface as a distinctly nameable procurement. Our keyword and full-text approach would miss such embedded demand. This explanation reduces the strength of the absence claim, and we flag it prominently. It does not, however, dissolve the finding, because the same embedding argument applies to public-key infrastructure and artificial intelligence, which nonetheless surface in large numbers, so the differential visibility of post-quantum cryptography relative to adjacent domains still requires explanation.

The third is that post-quantum cryptography is not yet a tracked category in some procurement systems, which is the most plausible reading of the zero we observe in World Bank-financed procurement, where a development-finance buyer may not yet classify or require quantum-safe cryptography at all. Under this reading the zero is informative about the diffusion of the mandate beyond the standard-setting jurisdictions rather than about activity within them.

These explanations are not mutually exclusive, and distinguishing among them is the natural next step, which we return to below. The measurement stands regardless of which combination holds: the visible, labelled, purchasable demand for post-quantum cryptography is very small relative to both the mandate and the adjacent domains, and the procurement record makes that smallness precise and watchable.

### 5.2 Policy implications

If the gap reflects a genuine lag, it is an early warning. The migration deadlines are fixed, the threat model front-loads the effective deadline through the harvest-now-decrypt-later dynamic, and the procurement pipeline for cryptographic infrastructure is not instantaneous. A procurement signal that remains near zero as the deadlines approach would be evidence that the mandate is not converting to purchasing at the rate the timeline requires. Making that signal continuously observable, which the live observatory does, gives policy-makers and oversight bodies an independent instrument for tracking readiness that does not depend on self-reported migration status.

If instead the gap reflects procurement invisibility, the implication is for procurement practice rather than for cryptographic policy: quantum-safe requirements embedded in unlabelled contracts are hard to audit, and a more explicit classification of cryptographic requirements in procurement notices would make the transition measurable and therefore governable. Either way, the case for treating cryptographic-migration demand as a first-class, labelled category in public procurement is strengthened by how faint the signal currently is.

### 5.3 The instrument

Beyond the specific finding, this article is a demonstration that the procurement record can be read as a cross-domain, cross-jurisdiction demand instrument, and that it can be read in a way whose provenance a reader can independently check. The anti-fabrication construction is not incidental to the argument. A claim about an absence is only as strong as the reader's confidence that the absence is not manufactured, and a pipeline in which every record carries a hash of its raw source and every statistic is recomputable from the published records gives that confidence a concrete basis.

## 6. Limitations

Coverage is a curated demand-signal sample and not a population census. The European Union source is the deepest, and the United States and United Kingdom sources undercount, so absolute cross-region comparisons are comparisons of visible procurement rather than of total spend, and our central within-region ratios are chosen precisely to avoid that pitfall. Domain tagging uses keyword and code matching and can both miss embedded demand, as Section 5.1 discusses, and, in principle, over-match on incidental mentions, though our within-domain buyer inspection did not surface such over-matching at a level that would change the finding. Monetary values exist only for the United States source. The corpus is a snapshot at the time of measurement and is designed to be re-harvested, so the figures here describe a dated build and will move as coverage deepens. Finally, procurement is a leading and partial indicator of migration and not a measure of migration itself, and we make no causal claim linking mandate to procurement.

## 7. Conclusion

We set out to measure whether the maturing mandate for post-quantum cryptography is yet visible in what governments buy. Using a live, provenance-verified corpus of 4,401 trust-technology procurement records across four domains and 106 countries, we find that post-quantum cryptography accounts for 1.14 percent of the corpus and for roughly one part in ninety of tagged United States federal award value, and that the smallness of the signal holds across every region and value measure we examine, against a backdrop of large and rising procurement of the adjacent trust technologies. We call this the quantum-readiness procurement gap. It is a descriptive finding, it admits several explanations that further work can distinguish, and it rests on a measurement whose provenance the reader can verify. The procurement record is an under-used instrument for observing the readiness of the state for the post-quantum transition, and, on the present evidence, that record shows a mandate that has not yet, in any visible way, reached the point of purchase.

## Data and code availability

The full corpus is published on Zenodo under a Creative Commons Attribution 4.0 licence, concept DOI 10.5281/zenodo.21192405, which resolves to the latest version. The harvesting, validation, consolidation and analysis pipeline, the source ledger, and this article's underlying figures are open at https://github.com/tyche-dev/trust-tech-procurement-observatory. The live observatory, from which every figure in this article can be reproduced, is at https://procurement.eatf.eu. Every statistic reported here is computed by the published analysis script from the committed records.

## Competing interests

The author declares no competing interests.
