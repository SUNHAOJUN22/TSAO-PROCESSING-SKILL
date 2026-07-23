# TSAO Process Intelligence OS

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.6-orange.svg)](CHANGELOG.md)

**Evidence → experiments → models → scale-up → process package → acceptance → field learning.**

TSAO turns a chemical-process question into a traceable, fail-closed development programme. A literature value is not a plant setpoint, a converged simulation is not approval, and a generated file is not completed physical work.

[中文](README.zh-CN.md) · [Execution contract](SKILL.md) · [Architecture](ARCHITECTURE.md) · [Capability matrix](docs/CAPABILITY_MATRIX.md)

## Routes

| Route | Current scope |
|---|---|
| `process-general` | reaction, properties, reactors, separation/recycle, control, HSE, reliability and scale-up |
| `epdm` | EPM/EPDM catalyst, terpolymerization, recovery, compounding and customer qualification |
| `poe` | **executable specialist alpha** for POE solution polymerization: 139-asset lineage, 12 modules, reference kinetics/property/case checks and content-level package audit |
| `polymer-general` | other polymerization, modification, formulation, reactive processing and recycling routes |

Every route inherits G0–G18 Gates, 14 workstreams, M0–M9 maturity, evidence states, model-risk controls and named human approval.

## Start

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root . --profile core
python -m tsao.cli route "POE solution polymerization and solvent recovery"
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
```

## POE alpha.6

The POE pack now includes:

- 139/139 audited source-asset identities, 18/18 requirements and seven real conflict/deviation records;
- twelve module contracts spanning CQA, catalyst/impurity, kinetics, properties, reactors, flowsheet, recycle, dynamics and acceptance;
- transparent reference kinetics, property-method qualification and simulator-neutral steady/dynamic case validation;
- a manifest/hash/content/cross-reference package auditor that rejects placeholders and maps Chinese legacy deliverables;
- synthetic/deidentified fixtures and adversarial tests without redistributing controlled Aspen, MATLAB, Origin or contract files.

See [POE status](skills/poe/STATUS.md) and the [P0 remediation report](reports/poe/POE_ALPHA6_P0_REMEDIATION.md).

## Verify

```bash
python scripts/run_ci.py
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse
python -m tsao.cli snapshot --root . --out TSAO-source.zip
python -m tsao.cli verify-archive --archive TSAO-source.zip
```

GitHub Actions is read-only. It validates the committed source identity on Ubuntu/Python 3.11–3.12, Windows/Python 3.12 and macOS/Python 3.12, verifies the POE wheel payload and builds a deterministic source snapshot. After intentional source changes, maintainers explicitly rebuild `reports/SOURCE_CORE_MANIFEST.tsv`, review the diff and run `doctor` again.

## Source identity

`doctor --profile core` verifies the committed source identity without modifying it. Refresh the manifest only after intentional changes:

```bash
python scripts/build_source_asset_manifest.py --root . --out reports/SOURCE_CORE_MANIFEST.tsv
python -m tsao.cli doctor --root . --profile core
```

Machine-readable identities: [source-core policy](reports/ALPHA6_SOURCE_CORE_STATUS.json), [complete distribution](reports/COMPLETE_DISTRIBUTION_REFERENCE.json) and [release](reports/RELEASE_IDENTITY.json).

## Trust boundary

The POE open software layer is `EXECUTABLE_SPECIALIST_ALPHA`; historical model execution and all scientific, engineering, safety, legal, customer and industrial approvals remain **`NOT_EVALUATED`** until supported by real evidence and named qualified approval.

`main` is the sole authoritative development line. Original TSAO code and documentation are Apache-2.0; inherited assets retain their recorded provenance and redistribution boundary in [NOTICE.md](NOTICE.md).
