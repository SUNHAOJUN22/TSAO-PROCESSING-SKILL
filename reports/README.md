# Reports

This directory contains machine- and human-readable qualification, release, migration and audit records. Every report must identify its source and distinguish software-artifact qualification from scientific, engineering, safety, legal, customer and industrial approval.

## Current identities

- `RELEASE_IDENTITY.json` — canonical alpha.6 release identity and approval boundary.
- `COMPLETE_DISTRIBUTION_REFERENCE.json` — qualified complete-distribution hash, test count and cleanroom result.
- `SOURCE_CORE_MANIFEST.tsv` — committed public-source identity verified by `tsao doctor --profile core`.
- `ALPHA6_SOURCE_CORE_STATUS.json` — source-core qualification request state; CI status remains external to the source tree.

## Runtime output

`scripts/run_ci.py` writes mutable execution output under `reports/runtime/`. Runtime logs and reports are intentionally excluded from frozen source manifests and release hashes. A release report becomes immutable only after it is copied to a versioned filename with its tested source identity.

## Historical audits

- `LINEAGE_COMPLETENESS_AUDIT_ALPHA3.md` compares the earliest SJTU-POE/universal-polymer mission, EPDM v9 and TSAO evolution.
- `CODE_AUDIT_ALPHA2.md` records the alpha.2 code-hardening work.
- `QUALIFICATION_BOUNDARY.md` defines what repository CI can and cannot approve.
