# TSAO Process Intelligence OS

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.7-orange.svg)](CHANGELOG.md)

**Evidence → experiments → models → scale-up → process package → acceptance → field learning.**

TSAO turns a chemical-process question into a traceable, fail-closed development programme. Literature values are not plant setpoints, simulation convergence is not approval, and generated files are not completed physical work.

[中文](README.zh-CN.md) · [Execution contract](SKILL.md) · [Architecture](ARCHITECTURE.md) · [Capability matrix](docs/CAPABILITY_MATRIX.md)

## Routes

| Route | Current scope |
|---|---|
| `process-general` | reaction, properties, reactors, separation/recycle, control, HSE, reliability and scale-up |
| `epdm` | EPM/EPDM catalyst, terpolymerization, recovery, compounding and customer qualification |
| `poe` | **executable specialist alpha with P1 references**: 139-asset lineage, twelve modules, kinetics/estimation/properties/reactors/dynamics/scale-up references and evidence audit v2 |
| `polymer-general` | other polymerization, modification, formulation, reactive processing and recycling |

All routes inherit G0–G18 Gates, fourteen workstreams, M0–M9 maturity, evidence states, model-risk controls and named human approval.

## Start

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root . --profile core
python -m tsao.cli route "POE solution polymerization and solvent recovery"
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
python -m tsao.cli poe status --root .
python -m tsao.cli poe reference-demo
```

## POE alpha.7

The POE pack contains:

- 139/139 controlled source-asset identities, 18/18 requirements and seven real conflicts/deviations;
- twelve machine-readable module contracts;
- transparent P0/P1 references for moment kinetics, bounded estimation and identifiability, properties/transport, PFR/CSTR, heat removal, FOPDT transitions, recycle memory and scale-up similarity;
- model-asset passports and a package auditor that checks content, hashes, structured records, evidence status, requirements, conflicts and approvals;
- deidentified/synthetic fixtures and adversarial tests without redistributing controlled Aspen, MATLAB, Origin, CFD or contract files;
- wheel payload plus installed-runtime verification.

See [POE status](skills/poe/STATUS.md) and [P1 remediation](reports/poe/POE_ALPHA7_P1_REMEDIATION.md).

## Verify

```bash
python scripts/run_ci.py
python skills/poe/scripts/audit_p0.py --root .
python skills/poe/scripts/audit_p1.py --root .
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse
python scripts/verify_wheel_runtime.py --wheel-dir wheelhouse
```

GitHub Actions runs the same read-only qualification on Ubuntu/Python 3.11–3.12, Windows/Python 3.12 and macOS/Python 3.12. The POE core-library branch-coverage gate is at least 75%; command wrappers are covered by end-to-end tests. Source identity is committed and verified; runtime reports stay outside the frozen manifest.

## Trust boundary

The POE open layer is `EXECUTABLE_SPECIALIST_ALPHA_P1_REFERENCE`. Historical commercial models and all scientific, engineering, HSE, legal, customer and industrial approvals remain **`NOT_EVALUATED`** until supported by active-project evidence and named qualified approval.

`main` is the sole authoritative branch. Original TSAO code and documentation are Apache-2.0; inherited assets retain their recorded provenance and redistribution boundary in [NOTICE.md](NOTICE.md).
