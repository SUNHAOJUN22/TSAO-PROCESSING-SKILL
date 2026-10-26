# Raw-data policy

Raw experimental and plant data are immutable, access-controlled and identified by checksum. Corrections are represented as new processed datasets with explicit transformation code and provenance.

Each dataset records source system, sampling boundary, time basis, units, instrument and calibration, analyst, exclusions, censoring, synchronization, missingness, preprocessing, train/validation allocation and permitted use. Confidential or export-controlled data must not enter the public repository.

Public synthetic-fixture distribution requires all four explicit classifications:
`confidentiality=PUBLIC`, `evidence_class=SYNTHETIC_PUBLIC_FIXTURE`,
`license_scope=PUBLIC_SYNTHETIC`, and the exact boolean
`public_fixture_eligible=true`. Unknown, blank, differently cased or unreviewed
labels remain blocked. The eligibility flag alone cannot authorize distribution.
This policy does not reclassify existing controlled records.
