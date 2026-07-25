# TSAO Process Intelligence OS

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%2B-2563eb)](pyproject.toml)
[![License](https://img.shields.io/badge/License-Apache--2.0-15803d)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha.8-d97706)](reports/QUALIFICATION_BOUNDARY.md)

**A traceable, fail-closed operating system for building and auditing chemical-process packages. EPDM is the flagship specialist route; POE is the evidence-rich specialist route.**

[简体中文](README.zh-CN.md) · [Architecture](ARCHITECTURE.md) · [Capability matrix](docs/CAPABILITY_MATRIX.md) · [Research integrity](docs/RESEARCH_INTEGRITY.md)

![TSAO Process Intelligence OS overview](docs/assets/readme/tsao-process-intelligence-os.svg)

## What TSAO is

TSAO turns a process-development brief into a controlled project workspace, a machine-readable process package and an auditable evidence trail. It is designed to make missing evidence visible before assumptions propagate into equipment sizing, control, safety, customer or investment decisions.

The repository currently provides three executable routes:

| Route | Executable scope | Current boundary |
|---|---|---|
| `tsao package` | Universal design basis, streams, equipment, mass/energy balances, controls, HSE, evidence, acceptance and approval audit | Executable alpha framework; project-specific engineering remains to be supplied and approved |
| `tsao epdm` | Active sites, E/P/diene kinetics, three-level models, architecture/gel risk, semibatch closure, heat/mixing, phase stability, recycle poison, devolatilization and process-package audit | Calculated reference layer; parameter fitting and industrial qualification are not bundled |
| `tsao poe` | P0/P1 POE reference kernel, kinetics/properties/reactors/dynamics/scale-up and 139-asset evidence lineage | Evidence-rich specialist alpha; historical assets remain controlled evidence |

![Universal process-package lifecycle](docs/assets/readme/universal-process-package.svg)

## Universal process-package platform

The general route covers the recurring structure of a process package rather than hard-coding one technology. Fourteen process-general modules and six workflows span:

- chemistry and reaction basis, measurement/data quality and thermodynamic method selection;
- reactors, transport, separation, recycle, utilities and material/energy closure;
- equipment records, process control, operability, abnormal scenarios and HSE;
- scale-up/pilot logic, TEA/LCA/supply interfaces and package acceptance;
- bioprocess, electrochemical, solids/crystallization, fine-batch and petrochemical extensions;
- evidence IDs, status gates, approval records and deterministic delivery archives.

![Layered process-package architecture](docs/assets/readme/process-package-architecture.svg)

### Process-package object model

A package is audited as a connected system, not a stack of unrelated documents:

```text
design basis
  ├─ streams and components
  ├─ equipment and operating envelopes
  ├─ mass / energy balances
  ├─ thermodynamic and model basis
  ├─ control / interlock / abnormal cases
  ├─ HSE and acceptance requirements
  └─ evidence ledger and named approvals
```

Unknown or unsupported claims produce `HOLD` or `FAIL`; they are never silently promoted to `PASS`.

## EPDM flagship specialist

EPDM adds a deeper mechanism-to-process chain on top of the universal package.

![EPDM multiscale chain](docs/assets/readme/epdm-multiscale-chain.svg)

The mandatory chain is:

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

| Level | Implemented reference calculations | Appropriate use |
|---|---|---|
| 1 — screening | active-site normalization, ternary insertion/transfer/deactivation, insertion fractions, pseudo-first-order conversion | rapid ranking and input sanity checks |
| 2 — engineering | Arrhenius temperature adjustment, residence-time conversion, conservative semibatch material/energy step, heat-removal margin, mixing Reynolds number, recycle-poison closure, devolatilization Damköhler number | flowsheet studies and experiment planning with explicit assumptions |
| 3 — detailed reference | heterogeneous site families, chain moments/dispersity reference, branch/gel risk, Flory–Huggins spinodal margin and heat-transfer entropy generation | deciding whether higher-fidelity PBM/CFD/EOS work is justified |

All three layers return `CALCULATED_REFERENCE_ONLY`. They do **not** claim fitted kinetics, licensed thermodynamics, qualified CFD, equipment design, HAZOP/LOPA/SIL approval, customer qualification or an industrial performance guarantee.

### EPDM process-package map

![EPDM process-package reference flowsheet](docs/assets/readme/epdm-process-flowsheet.svg)

The executable EPDM audit is fail-closed when any of the following remain open:

- the industrial catalyst benchmark is absent without an approved retirement record;
- active-site concentration or diene topology lacks evidence;
- heat-removal, high-viscosity mixing or polymer-solution phase stability is unqualified;
- recycle impurity/poison accumulation has no finite closure;
- devolatilization is represented without a non-equilibrium basis;
- the product bridge from raw polymer to customer line is incomplete;
- referenced EPDM evidence IDs are missing from the package ledger.

## Install and run

```bash
git clone https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL.git
cd TSAO-PROCESSING-SKILL
python -m pip install -e .[dev]
```

### Repository and source-identity check

```bash
python -m tsao.cli doctor --root . --profile core
```

### Create and audit a generic process workspace

```bash
python -m tsao.cli init \
  --brief examples/generic-process/brief.yaml \
  --out work/demo
python -m tsao.cli audit --root work/demo
python -m tsao.cli package template --family "continuous chemical process"
```

### Run EPDM references

```bash
python -m tsao.cli epdm status
python -m tsao.cli epdm reference-demo
python -m tsao.cli epdm model-suite --temperature-k 323.15 --residence-s 300
python -m tsao.cli epdm audit
```

`model-suite` emits the three kinetic levels, a conservative semibatch step, molar-closure residual, phase-stability margin, devolatilization Damköhler number and irreversible heat-transfer entropy generation.

### Run POE references

```bash
python -m tsao.cli poe status --root .
python -m tsao.cli poe audit-p0 --root .
python -m tsao.cli poe audit-p1 --root .
python -m tsao.cli poe reference-demo
```

## Evidence and gates

![Evidence and qualification gates](docs/assets/readme/evidence-gate-system.svg)

Every decision-facing result should retain:

1. the source or dataset ID;
2. measurement/model conditions and units;
3. the equation, method and validity boundary;
4. assumptions, uncertainty and conflict records;
5. current gate status and named approver where approval exists.

A software test can establish that code behaves as specified. It cannot establish that chemistry, equipment, safety, customer performance or plant economics are correct for a real project.

## Verification

![Verification pipeline](docs/assets/readme/verification-pipeline.svg)

Run the integrated local qualification:

```bash
python scripts/run_ci.py
python skills/epdm/scripts/audit_epdm.py
python skills/poe/scripts/audit_p0.py --root .
python skills/poe/scripts/audit_p1.py --root .
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse
python scripts/verify_wheel_runtime.py --wheel-dir wheelhouse
```

The CI workflow executes on Ubuntu/Python 3.11–3.12, Windows/Python 3.12 and macOS/Python 3.12. It checks compilation, tests, branch coverage, contracts, provenance, Ruff, EPDM/POE audits, wheel members, installed runtime, CLI smoke and deterministic README graphics.

The source manifest is part of release identity: changing a source file without rebuilding `reports/SOURCE_CORE_MANIFEST.tsv` is designed to fail the repository doctor.

## Repository map

```text
tsao/                       universal executable core and CLI
skills/process-general/     fourteen general process modules and workflows
skills/epdm/                flagship EPDM calculations, contracts and audits
skills/poe/                 POE specialist and controlled evidence lineage
skills/polymer-general/     reusable polymer planning and balance tools
schemas/                    cross-project contracts
examples/                   reproducible starter briefs
scripts/                    CI, provenance, packaging and graphics generation
docs/assets/readme/         original repository-owned AI-generated SVG diagrams
reports/                    qualification, lineage and consolidation records
tests/                      repository, security, schema and integration tests
```

Regenerate the documentation graphics deterministically with:

```bash
python scripts/generate_readme_assets.py
```

## Status language

| Status | Meaning |
|---|---|
| `PASS` | The declared software or evidence gate is satisfied |
| `HOLD` | Required evidence, qualification or approval is incomplete |
| `FAIL` | A schema, invariant, balance, reference or integrity rule is violated |
| `NOT_EVALUATED` | No qualified conclusion has been made |
| `CALCULATED_REFERENCE_ONLY` | A transparent example calculation, not a fitted or approved design result |

## Branch policy

`main` is the sole authoritative branch. Repository consolidation history is recorded in `reports/BRANCH_CONSOLIDATION_2026-07-23.md`. New development should preserve source identity, tests and evidence boundaries rather than creating parallel “more complete” lines that silently diverge.

## License and responsibility boundary

The code is licensed under Apache-2.0. Use of this repository does not replace qualified process engineering, laboratory work, equipment design, relief design, HAZOP/LOPA/SIL, legal review, environmental permitting, customer trials or operating approval.
