# TSAO Process Intelligence OS

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.5-orange.svg)](CHANGELOG.md)

**TSAO turns a chemical-process question into a traceable development programme: evidence → experiments → models → scale-up → process package → acceptance → field learning.**

TSAO is software-neutral and fail-closed. A paper, patent, simulation, generated file or successful test never becomes a plant setpoint or technical approval by itself.

[中文](README.zh-CN.md) · [Execution contract](SKILL.md) · [Architecture](ARCHITECTURE.md) · [Capability matrix](docs/CAPABILITY_MATRIX.md)

## Four routes

| Route | Scope |
|---|---|
| `process-general` | reaction, properties, reactors, separation/recycle, control, HSE, reliability and scale-up |
| `epdm` | EPM/EPDM catalyst-to-customer lifecycle |
| `poe` | POE solution-polymerization kinetics, flowsheet, dynamics, scale-up and acceptance |
| `polymer-general` | other polymerization, modification, formulation and recycling routes |

## One path to use it

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root .
python -m tsao.cli route "continuous catalytic reactor and solvent recovery"
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
```

`tsao init` creates G0–G18, 14 workstreams, **266 fail-closed work packages**, M0–M9 maturity records and explicit external-execution states.

AI agents read `SKILL.md`, then execute `prompts/TSAO_PROJECT_EXECUTION_PROMPT.md`.

## What is verified

- version, Schema, source/provenance and specialist integrity through `tsao doctor`;
- normal and adversarial tests for Gates, evidence, models, balances, scientific kernels, archives and project generation;
- deterministic release and cleanroom revalidation;
- Ubuntu/Python 3.11–3.12 plus Windows/macOS portability.

## Truthful boundary

Software qualification is not scientific, engineering, safety, legal, customer or industrial approval. Physical experiments, commercial simulation, relief design, HAZOP/LOPA/SIL, FTO, pilot/demonstration and plant guarantees remain `NOT_EVALUATED` until real evidence and named qualified approval exist.

## Map

- `SKILL.md` — non-negotiable operating contract
- `tsao/` — executable core and `doctor`
- `skills/` — four specialist packs
- `schemas/` — typed data and approval contracts
- `reports/SOURCE_CORE_MANIFEST.tsv` — public-source identity
- `reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv` — complete qualified distribution identity
- `scripts/` — audits, CI and release tools

Apache-2.0 for original TSAO code and documentation. See `NOTICE.md` for inherited-asset attribution and license isolation.
