# Reports

This directory separates immutable release/source identities from mutable runtime output. Software qualification never substitutes for scientific, engineering, HSE, legal, customer or industrial approval.

## Current alpha.7 identities

- `RELEASE_IDENTITY.json` — alpha.7 source/release boundary.
- `ALPHA7_SOURCE_CORE_STATUS.json` — external-verification policy for the committed source tree.
- `SOURCE_CORE_MANIFEST.tsv` — frozen public-source identity verified by `tsao doctor --profile core`.
- `COMPLETE_DISTRIBUTION_REFERENCE.json` — explicitly `NOT_EVALUATED` until the controlled alpha.7 complete distribution is rebuilt and cleanroom-qualified.
- `poe/POE_ALPHA7_P1_REMEDIATION.md` — POE P1 software remediation and remaining external Gates.

## Historical identities

- `history/COMPLETE_DISTRIBUTION_REFERENCE_ALPHA6.json` — qualified alpha.6 controlled complete distribution.
- `history/ALPHA6_SOURCE_CORE_STATUS.json` and `history/CI_RESULTS_BEFORE_RUNTIME_SPLIT.json` — frozen alpha.6 records.
- Alpha.6 POE P0 reports remain historical evidence of the preceding release.

## Runtime output

`scripts/run_ci.py` writes mutable execution output under `reports/runtime/`. Runtime files are excluded from frozen source and release manifests. Promote a result to a versioned report only with the exact tested source identity and approval boundary.
