# Main-only CI and AI visual upgrade — 2026-08-05

## Objective

Harden the sole `main` branch, remove temporary publication machinery, make the performance baseline stable across maintenance commits, and expand the bilingual README with governed AI-for-Science diagrams.

## Implemented design

- only `main` push and manual dispatch trigger permanent CI;
- superseded CI runs are cancelled;
- performance qualification uses an explicit Alpha.14 commit and verifies ancestry before benchmarking;
- eight new deterministic SVG diagrams extend the visual system from 21 to 29 assets;
- bilingual README, Skillpack inventory, Wheel content/runtime and accessibility contracts use the same asset count;
- one permanent workflow remains: `.github/workflows/ci.yml`;
- software qualification remains distinct from scientific, engineering, HSE, customer and industrial approval.

## Validation

Validation results are generated from the local qualified source snapshot before the atomic `main` update.

## Qualification results

- 364 tests collected and passed.
- Branch coverage: 77% (required minimum: 75%).
- EPDM adaptive numerical integration branch coverage: 91%.
- Repository Doctor: PASS for repository structure, version consistency, schemas, capabilities, source provenance and release identity.
- Capability audit: PASS.
- EPDM package audit: PASS.
- POE P0 audit: PASS.
- POE P1 audit: PASS_WITH_EXTERNAL_HOLDS; the pre-existing external execution boundaries remain explicit.
- Skillpack inventory: PASS with four Skills and 29 README SVG assets.
- SVG generation, deterministic regeneration, XML accessibility, external-resource prohibition and contrast checks: PASS for all 29 assets.
- Wheel build and content verification: PASS; the Wheel contains all 29 diagrams and the complete governed Skillpack tree.
- Isolated PIP_TARGET Wheel runtime: PASS.
- Standard-venv Wheel runtime was not completed in the local sandbox because its package index could not supply PyYAML; permanent GitHub CI retains this network-backed gate.
- Deterministic public-source snapshot: PASS with 410 governed manifest files and provenance/release-metadata self-validation.

These are software-artifact results only. Scientific, engineering, HSE, customer and industrial approvals remain `NOT_EVALUATED`.
