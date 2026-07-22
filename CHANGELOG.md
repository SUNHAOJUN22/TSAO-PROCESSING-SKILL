# Changelog

All notable changes are documented here. The project follows Semantic Versioning.

## 0.1.0-alpha.3 — 2026-07-22

### Restored and added

- Restored the original one-call execution contract, fourteen professional workstreams, evidence/claim states, accountable roles and M0–M9 maturity model in the root Skill.
- Added `skills/process-general/` so biochemical, electrochemical, solids, fine-chemical, petrochemical and generic process routes have an explicit specialist method instead of routing to an unimplemented domain label.
- Integrated `process-general` into project initialization, manifests and the project JSON Schema.
- Added lineage-completeness and subskill-content regression tests, including direct tests for POE, universal-polymer and non-polymer routing.
- Corrected the root `SKILL.md` and README version drift that remained after the alpha.2 code audit.

### Boundary

The GitHub source tree remains a reviewable core plus specialist contracts. The separately qualified complete distribution contains the full EPDM v9, SJTU-POE and universal-polymer source trees. Their historical data remain reference-only and all real technical approvals remain `NOT_EVALUATED`.

## 0.1.0-alpha.2 — 2026-07-21

### Fixed

- Split the original monolithic core into independently testable Gate, evidence, model, assurance, routing, science, project and archive modules while preserving the `tsao.core` compatibility surface.
- Made Gate transitions transactional and fail-closed; rejected noncanonical, duplicate and skipped Gate states.
- Made malformed dates, contradiction states and unknown model-risk/status values fail closed.
- Prevented route substring false positives and added numeric, finite, rectangular and sign validation to scientific kernels.
- Hardened project bootstrap/audit against non-mapping YAML, invalid manifests, hidden false approvals and symlinked template trees.
- Hardened deterministic ZIP creation and validation against source/output self-inclusion, symlinks, secret-like files, case collisions, path traversal, drive paths, compression bombs and member floods.
- Added structured CLI errors, archive verification, process-group timeout cleanup and strict repository/Schema regression tests.
- Fixed the GitHub Issue Form contract, pinned CI actions, aligned version metadata and unified compile/test/lint qualification.

### Validation boundary

Repository CI qualifies software artifacts only. Scientific, engineering, process-safety, legal, customer and industrial approvals remain `NOT_EVALUATED`.

## 0.1.0-alpha.1 — 2026-07-21

### Added

- TSAO Process Intelligence OS master skill and G0–G18 fail-closed lifecycle.
- Typed Gate, evidence, model-risk and assurance-graph contracts.
- Runnable Python package and CLI for routing, project initialization, audit and deterministic packaging.
- EPDM, POE and universal-polymer specialist subskills under one governance layer.
- JSON Schemas for projects, evidence and Gate records.
- Scientific, governance, adversarial and end-to-end tests.
- GitHub Actions CI for Python 3.11 and 3.12.
- Apache-2.0 licensing, notices, security, governance and contribution policies.
- Autonomous refinement and full project-execution prompts.

### Qualification

The independently built full distribution passed 362 tests and cleanroom archive validation. Repository CI qualifies software artifacts only. Scientific, engineering, customer and industrial approvals remain `NOT_EVALUATED`.
