# Reports

This directory separates immutable release/source identities from mutable runtime output. Software qualification never substitutes for scientific, engineering, HSE, legal, customer or industrial approval.

## Current alpha.9 identities

- `RELEASE_IDENTITY.json` — alpha.9 source/release boundary and current source-status pointer.
- `ALPHA9_SOURCE_CORE_STATUS.json` — qualified public source, four-Skill, sixteen-diagram and isolated-install status.
- `SOURCE_CORE_MANIFEST.tsv` — frozen public-source identity verified by `tsao doctor --profile core`.
- `COMPLETE_DISTRIBUTION_REFERENCE.json` — explicitly `NOT_EVALUATED` until the controlled complete distribution, including excluded historical binaries, is rebuilt and cleanroom-qualified for alpha.9.
- `FINAL_AUDIT_REPORT.md` — latest repository, Wheel, CI, branch and responsibility-boundary audit.
- `poe/POE_ALPHA7_P1_REMEDIATION.md` — POE P1 remediation history and remaining external Gates.

## Historical identities

- `ALPHA8_SOURCE_CORE_STATUS.json` and `ALPHA8_PROCESS_PACKAGE_EPDM_REMEDIATION.md` — frozen alpha.8 records.
- `ALPHA7_SOURCE_CORE_STATUS.json` — frozen alpha.7 source identity.
- `history/COMPLETE_DISTRIBUTION_REFERENCE_ALPHA6.json` — qualified alpha.6 controlled complete distribution.
- `history/ALPHA6_SOURCE_CORE_STATUS.json` and `history/CI_RESULTS_BEFORE_RUNTIME_SPLIT.json` — frozen alpha.6 records.
- Alpha.6 POE P0 reports remain historical evidence of the preceding release.

## Runtime output

`scripts/run_ci.py` writes mutable execution output under `reports/runtime/`. Runtime files are excluded from frozen source and release manifests. Promote a result to a versioned report only with the exact tested source identity and approval boundary.
