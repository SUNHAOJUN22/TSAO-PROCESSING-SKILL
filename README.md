# TSAO Process Intelligence OS

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Stage](https://img.shields.io/badge/stage-0.1.0--alpha.5-orange.svg)](CHANGELOG.md)

**Traceable · Scientific · Auditable · Operational**

TSAO turns a chemical-process brief, evidence corpus, dataset, model or plant package into a fail-closed development programme:

`evidence → chemistry → measurement → properties/kinetics → reactor → separation/recycle → lab → bench → pilot → industrial design → control/HSE → qualification → technology package → transfer → field learning`

It creates auditable artifacts; it does not invent experimental, safety, legal or industrial approval.

[中文](README.zh-CN.md) · [Skill](SKILL.md) · [Architecture](ARCHITECTURE.md) · [Capability matrix](docs/CAPABILITY_MATRIX.md)

## Start here

```bash
python -m pip install -e .[dev]
tsao doctor
tsao init --brief examples/generic-process/brief.yaml --out work/demo
tsao audit --root work/demo
```

`tsao doctor` is the single health check for versions, schemas, specialist skills, provenance, release metadata, caches and approval boundaries.

## Four specialist routes

| Route | Use it for |
|---|---|
| `process-general` | catalytic, petrochemical, fine-chemical, biochemical, electrochemical, crystallization/solids and generic processes |
| `epdm` | EPDM catalyst, E/P/diene polymerization, recovery, compounding, product and customer qualification |
| `poe` | POE solution polymerization, properties, flowsheet, dynamics, scale-up and acceptance |
| `polymer-general` | other polymerization mechanisms, formulations, modification and reactive processing |

Routing keeps the master G0–G18 lifecycle, 14 workstreams and M0–M9 maturity model active.

## What one initialization creates

- G0–G18 Gate register and 266 fail-closed work packages;
- evidence, claim, assumption and contradiction records;
- experiment, model, scale-up and external-execution contracts;
- process-package, acceptance, transfer and field-learning structure;
- `NOT_EVALUATED` status for all work not backed by real evidence and named approval.

## Verify

```bash
python scripts/run_ci.py
python scripts/audit_capabilities.py
python -m tsao.cli verify-archive --archive TSAO-PROCESSING-SKILL.zip
```

The complete distribution includes the full inherited EPDM v9, SJTU-POE and universal-polymer source trees. The complete ZIP carries a per-file provenance ledger; the public branch carries a family-level parity ledger and exact release identity. `reports/SOURCE_PARITY_ALPHA5.json` states the public-repository parity status without pretending that a partial sync is complete.

## Boundary

A green CI qualifies the software artifact only. Catalyst synthesis, physical experiments, commercial simulation, equipment/relief design, HAZOP/LOPA/SIL, legal FTO, customer qualification, pilot/demonstration and industrial guarantees remain **`NOT_EVALUATED`** until project-specific evidence and named qualified approval exist.
