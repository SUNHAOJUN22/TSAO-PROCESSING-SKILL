# TSAO Process Intelligence OS

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.6-orange.svg)](CHANGELOG.md)

**Turn a chemical-process question into an auditable programme: evidence → experiments → models → scale-up → process package → acceptance → field learning.**

TSAO is software-neutral and fail-closed. A literature value is not a plant setpoint, a converged simulation is not approval, and a generated file is not completed physical work.

[中文](README.zh-CN.md) · [Execution contract](SKILL.md) · [Architecture](ARCHITECTURE.md) · [Capability matrix](docs/CAPABILITY_MATRIX.md)

## Choose a route

| Route | Scope |
|---|---|
| `process-general` | reaction, properties, reactors, separation/recycle, control, HSE, reliability and scale-up |
| `epdm` | EPM/EPDM catalyst, terpolymerization, recovery, compounding and customer qualification |
| `poe` | POE solution polymerization, properties, flowsheet, dynamics, scale-up and acceptance |
| `polymer-general` | other polymerization, modification, formulation, reactive processing and recycling routes |

Every route inherits G0–G18 Gates, 14 professional workstreams, M0–M9 maturity, evidence states, model-risk controls and named human approval.

## Start

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root . --profile core
python -m tsao.cli route "continuous catalytic reactor and solvent recovery"
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
```

`tsao init` creates 19 × 14 = **266 fail-closed work packages**, maturity records and explicit external-execution states.

## Verify

```bash
python scripts/run_ci.py
python -m tsao.cli snapshot --root . --out TSAO-source.zip
python -m tsao.cli verify-archive --archive TSAO-source.zip
```

- `doctor --profile core` verifies the GitHub source tree and `reports/SOURCE_CORE_MANIFEST.tsv`.
- `doctor --profile full` additionally verifies `reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv`, `FILE_MANIFEST.tsv`, `checksums.sha256` and `SBOM.json`.
- GitHub Actions runs the canonical qualification on Ubuntu/Python 3.11–3.12, Windows/Python 3.12 and macOS/Python 3.12, builds a wheel and publishes a deterministic source snapshot.
- The current machine-readable release record is [reports/RELEASE_IDENTITY.json](reports/RELEASE_IDENTITY.json).

## Repository map

- `SKILL.md` — non-negotiable execution contract
- `tsao/` — router, project generator, audits, integrity checks and CLI
- `skills/` — process-general, EPDM, POE and polymer-general packs
- `schemas/` — typed evidence, Gate, work-package, maturity and approval contracts
- `reports/` — source identities, qualification and release records
- `scripts/` — CI, provenance, snapshot and release tooling

`main` is the sole authoritative development line. The public source snapshot and the qualified complete distribution are separate, explicitly identified artifacts; see [source parity](docs/SOURCE_PARITY.md).

## Trust boundary

Software qualification is not scientific, engineering, safety, legal, customer or industrial approval. Physical experiments, commercial simulation, equipment and relief design, HAZOP/LOPA/SIL, FTO, pilot/demonstration work, customer qualification and plant guarantees remain **`NOT_EVALUATED`** until supported by real evidence and named qualified approval.

Original TSAO code and documentation are Apache-2.0. Inherited assets keep their recorded provenance and redistribution boundary; see [NOTICE.md](NOTICE.md).
