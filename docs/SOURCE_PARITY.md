# Source parity and release identity

TSAO publishes two software artifacts and never treats them as interchangeable.

## Public source snapshot

- Source of truth: `main`.
- Manifest: `reports/SOURCE_CORE_MANIFEST.tsv`.
- Verification: `python -m tsao.cli doctor --root . --profile core`.
- Build: `python -m tsao.cli snapshot --root . --out TSAO-source.zip`.
- Purpose: reviewable open-source implementation, specialist contracts, tests and documentation.

## Qualified complete distribution

- Manifest: `reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv`.
- Internal integrity: `FILE_MANIFEST.tsv`, `checksums.sha256`, `SBOM.json`.
- Verification: `python -m tsao.cli doctor --root . --profile full` plus cleanroom extraction CI.
- Purpose: public source plus controlled inherited EPDM v9, SJTU-POE and universal-polymer assets and historical identities.

The complete manifest can be stored in the public repository as an identity record even when controlled binary archives are distributed separately. A manifest entry does not change the file's ownership or license; `artifact_class` and `license_scope` remain authoritative.

## Technical approval

Neither software artifact approves chemistry, equipment, process safety, legal FTO, customer performance or a plant guarantee. Those states remain `NOT_EVALUATED` until project-specific evidence and named qualified approval exist.

Any missing path, duplicate path, unsafe path, size mismatch, SHA-256 mismatch, SBOM disagreement or false approval blocks qualification.
