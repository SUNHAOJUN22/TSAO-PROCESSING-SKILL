# TSAO Process Intelligence OS

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.5-orange.svg)](CHANGELOG.md)

**Turn a chemical-process question into a traceable development programme: evidence → experiments → models → scale-up → process package → acceptance → field learning.**

TSAO is software-neutral and fail-closed. Literature, patents, simulations, generated files and passing software tests never become plant setpoints or technical approvals by themselves.

[中文](README.zh-CN.md) · [Execution contract](SKILL.md) · [Architecture](ARCHITECTURE.md) · [Capability matrix](docs/CAPABILITY_MATRIX.md)

## Choose one route

| Route | Scope |
|---|---|
| `process-general` | reaction, properties, reactors, separation/recycle, control, HSE, reliability and scale-up |
| `epdm` | EPM/EPDM catalyst-to-customer lifecycle |
| `poe` | POE solution-polymerization kinetics, flowsheet, dynamics, scale-up and acceptance |
| `polymer-general` | other polymerization, modification, formulation and recycling routes |

All routes inherit the same G0–G18 Gates, evidence states, model-risk controls, uncertainty rules and human approval boundary.

## Start here

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root .
python -m tsao.cli route "continuous catalytic reactor and solvent recovery"
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
```

`tsao init` creates G0–G18, 14 professional workstreams, **266 fail-closed work packages**, M0–M9 maturity records and explicit external-execution states.

AI agents read `SKILL.md`, then execute `prompts/TSAO_PROJECT_EXECUTION_PROMPT.md`.

## Verify the repository

Run the same core qualification locally:

```bash
python scripts/run_ci.py
```

The gate compiles the source, runs the root and specialist test suites, audits capabilities, verifies repository provenance with `tsao doctor`, and applies Ruff. GitHub Actions repeats the gate on Ubuntu/Python 3.11–3.12, Windows/Python 3.12 and macOS/Python 3.12, then builds a wheel and runs CLI smoke tests.

## What the repository contains

- `SKILL.md` — non-negotiable operating contract
- `tsao/` — executable core, router, project generator, audits and `doctor`
- `skills/` — process-general, EPDM, POE and polymer-general specialist packs
- `schemas/` — typed evidence, Gate, work-package, maturity and approval contracts
- `reports/SOURCE_CORE_MANIFEST.tsv` — public-source identity
- `reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv` — complete qualified-distribution identity
- `scripts/` — local CI, capability and provenance tooling

The authoritative development line is `main`; release identity, source lineage and inherited-asset boundaries are documented rather than hidden in extra branches.

## Trust boundary

Software qualification is not scientific, engineering, safety, legal, customer or industrial approval. Physical experiments, commercial simulation, equipment and relief design, HAZOP/LOPA/SIL, FTO, pilot/demonstration work, customer qualification and plant guarantees remain `NOT_EVALUATED` until real evidence and named qualified approval exist.

Original TSAO code and documentation are Apache-2.0. See [NOTICE.md](NOTICE.md) and [source parity](docs/SOURCE_PARITY.md) for inherited-asset attribution and distribution boundaries.
