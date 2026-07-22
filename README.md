# TSAO Process Intelligence OS

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.4-orange.svg)](CHANGELOG.md)

**TSAO turns a chemical-process question into a traceable development programme — from evidence and experiments to models, scale-up, process package, acceptance and field learning.**

TSAO = **Traceable · Scientific · Auditable · Operational**. It is software-neutral and fail-closed: a plan, simulation or generated report never becomes technical approval by itself.

[中文](README.zh-CN.md) · [Skill contract](SKILL.md) · [Architecture](ARCHITECTURE.md) · [Roadmap](ROADMAP.md) · [Capability matrix](docs/CAPABILITY_MATRIX.md)

## Use it for

- greenfield process development, replication and localization;
- catalyst/route/product development and scale-up;
- retrofit, debottlenecking, troubleshooting and package audit;
- polymer, petrochemical, fine-chemical, biochemical, electrochemical, solids and formulation processes.

## One operating system, four specialist routes

| Route | Use for | Depth |
|---|---|---|
| `process-general` | reaction, property, reactor, separation, control, HSE and scale-up outside a polymer-specific pack | 14 structured domain modules |
| `epdm` | catalyst-to-customer EPM/EPDM development | full qualified v9 inheritance |
| `poe` | SJTU-derived POE solution-polymerization process packages | full kinetics/flowsheet/dynamics/acceptance source tree |
| `polymer-general` | other polymerization, modification and formulation routes | mechanism-neutral lifecycle pack |

## What one invocation produces

`brief → route → 19 Gates × 14 workstreams → evidence/hypotheses → experiments/models → lab/bench/pilot/demo → industrial package → acceptance/transfer`

`tsao init` immediately creates **266 fail-closed work packages**, the G0–G18 Gate set, an M0–M9 maturity record and explicit external-execution states.

## Quick start

```bash
python -m pip install -e .[dev]
python -m tsao.cli route "continuous catalytic reactor and solvent recovery"
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
python scripts/run_ci.py
```

AI agents should read `SKILL.md`, then execute `prompts/TSAO_PROJECT_EXECUTION_PROMPT.md`.

## Quality model

TSAO blocks a Gate when evidence is stale or contradictory, a model is unidentifiable or outside its domain, balances fail, scale-up similarity is unstated, external reviews are unexecuted, or an approval lacks evidence and a named approver.

The repository includes positive and adversarial tests for Gate transitions, evidence, model risk, balances, scientific kernels, project generation, specialist lineage, malicious ZIPs, deterministic builds and cleanroom revalidation.

## Truthful boundary

Repository CI qualifies **software artifacts only**. Chemistry, equipment, controls, relief design, HAZOP/LOPA/SIL, FTO, customer qualification, pilot operation and industrial performance remain `NOT_EVALUATED` until real evidence and qualified human approval exist.

## Project map

- `SKILL.md` — non-negotiable execution contract
- `tsao/` — machine-executable core
- `skills/` — four specialist packs
- `schemas/` — project, evidence, model, scale-up and acceptance contracts
- `templates/` — reusable project artifacts
- `scripts/` — audits, CI and deterministic release
- `vendor/releases/` — controlled inherited release identities

Apache-2.0 for original TSAO code and documentation. See `NOTICE.md` for attribution and license isolation.
