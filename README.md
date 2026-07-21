# TSAO Process Intelligence OS

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.1-orange.svg)](CHANGELOG.md)

**TSAO-PROCESSING-SKILL** is an open-source, software-neutral operating system for chemical-process research, development, scale-up, qualification and technology transfer.

TSAO means **Traceable · Scientific · Auditable · Operational**. The project is designed to turn an engineering brief, literature corpus, experimental dataset or existing plant package into a controlled research and industrialization program—not into an unverified answer dump.

[中文说明](README.zh-CN.md) · [Architecture](ARCHITECTURE.md) · [Skill entrypoint](SKILL.md) · [Roadmap](ROADMAP.md)

## What it does

The master skill orchestrates the full lifecycle:

`need → evidence → chemistry → measurement → properties → kinetics → reactor → separation/recycle → lab → bench → pilot → demonstration → industrial design → control → safety/reliability → TEA/LCA/IP → qualification → technology package → transfer → field learning`

It supports polymerization, catalytic and non-catalytic reaction systems, petrochemicals, fine chemicals, biochemical and electrochemical processes, solids handling, formulation, separations, utilities, retrofit, debottlenecking and third-party package review.

## Included specialist skills

| Specialist | Location | Role |
|---|---|---|
| EPDM | `skills/epdm/` | Full EPM/EPDM catalyst-to-customer lifecycle, inherited from the qualification-oriented v9 release |
| POE | `skills/poe/` | SJTU-derived solution-polymerization kinetics, flowsheet, dynamics, scale-up and acceptance methodology |
| General polymer development | `skills/polymer-general/` | Route-neutral polymer R&D and industrialization framework |

Historical case parameters are reference-only and can never become a new project design basis without project-specific validation.

## Open engineering ecosystem

TSAO uses adapters and contracts rather than a single simulator. It can route work to DWSIM/CAPE-OPEN, IDAES, Cantera, Pyomo, CoolProp, commercial simulators, CFD/FEM/PBM/DEM tools, Python, MATLAB, spreadsheets and laboratory systems. Tool output remains provisional until conservation, known-solution, limit-behaviour, uncertainty and applicability-domain checks pass.

## Quick start

```bash
python -m pip install -e .[dev]
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
python scripts/run_ci.py
```

For an AI agent, open `SKILL.md` and execute `prompts/TSAO_PROJECT_EXECUTION_PROMPT.md`.

## Qualification boundary

A green repository CI means the **software artifact** is internally consistent. It does not approve chemistry, equipment, controls, process safety, FTO, customer performance or a plant guarantee. Those states default to `NOT_EVALUATED` and require named qualified humans and real evidence.

## License and attribution

Original TSAO code and documentation are Apache-2.0. Upstream projects are referenced or adapted only through license-compatible interfaces. See `NOTICE.md`.