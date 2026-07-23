# Source parity and distribution identity

TSAO keeps two machine-readable identities because the public GitHub source core and the qualified complete distribution are not interchangeable artifacts.

- `reports/SOURCE_CORE_MANIFEST.tsv` records files that are browseable and reviewable on the GitHub branch.
- `reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv` records the qualified complete distribution, including inherited specialist assets and controlled historical binaries.

`tsao doctor --profile core` verifies the public source manifest. `tsao doctor --profile full` additionally requires the complete-distribution markers `FILE_MANIFEST.tsv`, `checksums.sha256` and `SBOM.json` and then verifies the complete manifest.

A missing path or size/SHA-256 mismatch fails the doctor check. Controlled binary releases support reproducibility but never substitute for reviewable source or project-specific technical validation. Numerical values in inherited cases remain reference-only until the active project validates identity, units, measurement boundary, property method and applicability.
