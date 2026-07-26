# TSAO Process Intelligence OS

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-2563eb)](pyproject.toml)
[![License](https://img.shields.io/badge/License-Apache--2.0-15803d)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha.8-d97706)](reports/QUALIFICATION_BOUNDARY.md)

**A traceable, fail-closed Skill platform for chemical-process packages. EPDM is the deepest flagship route; POE is the evidence-rich specialist route.**

[简体中文](README.zh-CN.md) · [Architecture](ARCHITECTURE.md) · [Capability matrix](docs/CAPABILITY_MATRIX.md) · [Research integrity](docs/RESEARCH_INTEGRITY.md)

![TSAO Process Intelligence OS overview](docs/assets/readme/tsao-process-intelligence-os.svg)

## One platform, four delivered Skills

| Skill | Executable or delivered scope | Truthful boundary |
|---|---|---|
| `process-general` | universal process-package contracts, 14 modules and 6 workflows | project engineering data and approvals remain external |
| `epdm` | active sites, E/P/diene kinetics, three model levels, semibatch closure, phase/mixing/heat, recycle poison and devolatilization | reference calculations, not industrial parameter certification |
| `poe` | P0/P1 reference kernels and controlled lineage for 139 historical assets | specialist alpha with explicit evidence boundaries |
| `polymer-general` | reusable evidence, balance, DoE, planning and scale-up utilities | generic planning tools, not a qualified product recipe |

The source checkout and the installed Wheel expose the same four-Skill inventory. Run:

```bash
python -m tsao.skillpacks --root .
# after Wheel installation:
tsao-skillpacks
```

The inventory fails closed unless the four Skills, 14 general-process modules, 6 workflows, 6 polymer-general scripts and at least 12 README diagrams are present.

![Universal process-package lifecycle](docs/assets/readme/universal-process-package.svg)

## Universal process-package platform

The general route models a process package as a connected engineering system rather than a document bundle. It covers chemistry, measurements, thermodynamics, reactors, transport, separation, recycle, utilities, equipment, control, abnormal cases, HSE, scale-up, TEA/LCA and acceptance. Domain overlays extend the same contract to polymer, bioprocess, electrochemical, solids/crystallization, fine-batch and petrochemical work.

![Layered process-package architecture](docs/assets/readme/process-package-architecture.svg)

### Connected data model

![Universal process-package data model](docs/assets/readme/process-package-data-model.svg)

```text
design basis
  ├─ streams and components
  ├─ equipment and operating envelopes
  ├─ mass / component / energy balances
  ├─ thermodynamic and model basis
  ├─ controls / alarms / interlocks / abnormal cases
  ├─ HSE and acceptance requirements
  └─ evidence ledger and named approvals
```

Unknown or unsupported claims produce `HOLD` or `FAIL`; they are never silently promoted to `PASS`.

## EPDM flagship specialist

EPDM adds a deeper mechanism-to-package chain on top of the universal platform.

![EPDM multiscale chain](docs/assets/readme/epdm-multiscale-chain.svg)

### Catalyst and kinetic network

![EPDM catalyst-to-architecture network](docs/assets/readme/epdm-catalyst-kinetics-network.svg)

```text
application / CQA
→ catalyst benchmark and active-site evidence
→ E/P/diene insertion, transfer, deactivation and poison memory
→ sequence, MWD/CCD, retained unsaturation, branching and gel risk
→ phase stability, viscosity, mixing, residence time and heat removal
→ quench, deashing, devolatilization, solvent/monomer recovery and purge
→ raw polymer, compound, cure, part durability and customer-line evidence
→ process-package acceptance
```

### Three model levels

![Three EPDM model levels](docs/assets/readme/epdm-three-level-models.svg)

| Level | Implemented reference calculations | Use |
|---|---|---|
| 1 — screening | active-site normalization, ternary propagation/transfer/deactivation, insertion fractions and rapid conversions | ranking and input checks |
| 2 — engineering | Arrhenius adjustment, residence-time conversion, conservative semibatch material/energy step, heat/mixing, recycle poison and devolatilization Damköhler number | flowsheet studies and experiment planning |
| 3 — detailed reference | heterogeneous site families, chain moments/dispersity, branching/gel, Flory–Huggins stability and heat-transfer entropy generation | deciding whether PBM/CFD/EOS work is justified |

![EPDM reactor-mode decision map](docs/assets/readme/epdm-reactor-mode-map.svg)

Every level returns `CALCULATED_REFERENCE_ONLY`. It does not claim fitted kinetics, licensed thermodynamics, qualified CFD, equipment design, HAZOP/LOPA/SIL approval, customer qualification or an industrial guarantee.

### Process, finishing and recycle

![EPDM process-package reference flowsheet](docs/assets/readme/epdm-process-flowsheet.svg)

![EPDM recovery, recycle and impurity-risk loop](docs/assets/readme/recovery-recycle-risk-loop.svg)

The EPDM audit fails closed when active-site evidence, diene topology, heat removal, high-viscosity mixing, phase stability, recycle-poison closure, non-equilibrium devolatilization or the raw-polymer-to-customer bridge is incomplete.

## Install and run

```bash
git clone https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL.git
cd TSAO-PROCESSING-SKILL
python -m pip install -e .[dev]
python -m tsao.cli doctor --root . --profile core
python -m tsao.skillpacks --root .
```

### Generic process package

```bash
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
python -m tsao.cli package template --family "continuous chemical process"
```

### EPDM

```bash
python -m tsao.cli epdm status
python -m tsao.cli epdm reference-demo
python -m tsao.cli epdm model-suite --temperature-k 323.15 --residence-s 300
python -m tsao.cli epdm audit
```

### POE

```bash
python -m tsao.cli poe status --root .
python -m tsao.cli poe audit-p0 --root .
python -m tsao.cli poe audit-p1 --root .
python -m tsao.cli poe reference-demo
```

## Evidence and qualification

![Evidence and qualification gates](docs/assets/readme/evidence-gate-system.svg)

Decision-facing results retain source IDs, conditions, units, method boundaries, assumptions, uncertainty, conflicts and the current Gate. Software tests establish software behavior only; they do not approve chemistry, equipment, safety, customer performance or plant economics.

## Verification and Wheel delivery

![Verification pipeline](docs/assets/readme/verification-pipeline.svg)

```bash
python scripts/generate_readme_assets.py
python scripts/generate_extended_readme_assets.py
python scripts/run_ci.py
python skills/epdm/scripts/audit_epdm.py
python skills/poe/scripts/audit_p0.py --root .
python skills/poe/scripts/audit_p1.py --root .
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse
python scripts/verify_wheel_runtime.py --wheel-dir wheelhouse
```

Wheel verification now has two independent gates:

1. **content gate:** requires the executable core plus the complete installed four-Skill tree, contracts, schemas, examples and all 12 diagrams;
2. **installation gate:** performs a real `pip install --target`, imports from that installed target, resolves the installed Skillpack data root and runs known-solution EPDM/POE/universal checks.

CI covers Ubuntu/Python 3.11–3.12, Windows/Python 3.12 and macOS/Python 3.12. It checks compilation, tests, branch coverage, contracts, provenance, Ruff, EPDM/POE audits, deterministic graphics, Wheel members, real installed runtime and CLI smoke.

The source manifest is part of release identity: a source change without the matching `reports/SOURCE_CORE_MANIFEST.tsv` update is designed to fail the repository doctor.

## Repository map

```text
tsao/                       universal executable core, CLI and Skillpack inventory
skills/process-general/     14 general-process modules and 6 workflows
skills/epdm/                flagship EPDM calculations, contracts and audits
skills/poe/                 POE specialist and controlled evidence lineage
skills/polymer-general/     reusable polymer planning and balance tools
schemas/                    machine-readable cross-project contracts
scripts/                    CI, provenance, packaging and graphics generation
docs/assets/readme/         deterministic repository-owned SVG diagrams
reports/                    qualification, lineage and consolidation records
tests/                      repository, security, schema and integration tests
```

## Status language

| Status | Meaning |
|---|---|
| `PASS` | declared software or evidence Gate is satisfied |
| `HOLD` | required evidence, qualification or approval is incomplete |
| `FAIL` | schema, balance, invariant, reference or integrity rule is violated |
| `NOT_EVALUATED` | no qualified conclusion has been made |
| `CALCULATED_REFERENCE_ONLY` | transparent calculation, not a fitted or approved design result |

## Branch and responsibility policy

`main` is the sole authoritative branch. The consolidation record is in [reports/BRANCH_CONSOLIDATION_2026-07-23.md](reports/BRANCH_CONSOLIDATION_2026-07-23.md). This repository does not replace qualified process engineering, laboratory work, equipment/relief design, HAZOP/LOPA/SIL, legal review, environmental permitting, customer trials or operating approval.
