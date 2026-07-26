# TSAO Process Intelligence OS

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11%E2%80%933.14-2563eb)](pyproject.toml)
[![License](https://img.shields.io/badge/License-Apache--2.0-15803d)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha.10-d97706)](reports/QUALIFICATION_BOUNDARY.md)

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

The source checkout and installed Wheel expose the same inventory:

```bash
python -m tsao.skillpacks --root .
# after Wheel installation:
tsao-skillpacks
```

The inventory fails closed unless the four Skills, 14 general-process modules, 6 workflows, 6 polymer-general scripts and at least 16 README diagrams are present.

![Universal process-package lifecycle](docs/assets/readme/universal-process-package.svg)

## Universal process-package platform

The general route treats a process package as a connected engineering system. It covers chemistry, measurements, thermodynamics, reactors, transport, separation, recycle, utilities, equipment, control, abnormal cases, HSE, scale-up, TEA/LCA and acceptance. The same contract extends to polymer, bioprocess, electrochemical, solids/crystallization, fine-batch and petrochemical work.

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

### Control, safety and simulator-neutral interfaces

![Control, interlock and process-safety chain](docs/assets/readme/control-safety-cause-effect.svg)

![Simulator-neutral integration contract](docs/assets/readme/simulation-integration-contract.svg)

The platform structures alarms, interlocks, Cause & Effect, abnormal response and HAZID/HAZOP/LOPA/SIL interfaces. Aspen Plus, Aspen HYSYS, DWSIM, custom models and DCS/PLC exchanges remain governed by the same design basis, evidence ledger and model passport; simulator convergence is not qualification.

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

### Identifiability, uncertainty and product evidence

![EPDM parameter identifiability and uncertainty ladder](docs/assets/readme/epdm-identifiability-uncertainty.svg)

![EPDM raw-polymer-to-customer evidence bridge](docs/assets/readme/epdm-product-customer-bridge.svg)

Parameters remain classified as measured, estimated, literature-prior, nuisance, fixed or non-identifiable. A reactor result cannot become a durability or customer claim without controlled compound, cure, part and line evidence.

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

## Measured performance and reproducibility

Performance claims are versioned software evidence, not engineering or industrial qualification. The release harness uses `timeit.repeat` medians for timing, `cProfile` for hotspot attribution and SHA-256 result digests to reject numerical drift.

```bash
python scripts/benchmark_performance.py --repeats 7 --output reports/runtime/PERFORMANCE_RESULTS.json
python scripts/compare_performance.py \
  --baseline reports/PERFORMANCE_BASELINE_ALPHA9.json \
  --current reports/runtime/PERFORMANCE_RESULTS.json \
  --output reports/runtime/PERFORMANCE_COMPARISON.json
python scripts/update_performance_readme.py \
  --comparison reports/PERFORMANCE_COMPARISON_ALPHA10.json --check
```

<!-- PERFORMANCE_RESULTS_START -->
| Workload | Baseline median | Optimized median | Speedup | Result identity |
|---|---:|---:|---:|---|
| EPDM three-level model, 64 site families | 596.09 µs | 129.38 µs | 4.61× | match |
| EPDM semibatch material-energy step | 21.78 µs | 13.29 µs | 1.64× | match |
| POE RK4, 400 steps | 31.76 ms | 13.76 ms | 2.31× | match |
| Universal process package, 500 equipment items | 4.18 ms | 4.42 ms | 0.95× | match |
| Source identity, 300 files build + verify | 45.13 ms | 23.21 ms | 1.94× | match |
<!-- PERFORMANCE_RESULTS_END -->

The gate requires identical result digests. EPDM site-family and semibatch workloads, POE RK4 and source-identity verification also have explicit minimum speedups; the 500-equipment universal package workload has a no-material-regression floor.

## Evidence and qualification

![Evidence and qualification gates](docs/assets/readme/evidence-gate-system.svg)

Decision-facing results retain source IDs, conditions, units, method boundaries, assumptions, uncertainty, conflicts and the current Gate. Software tests establish software behavior only; they do not approve chemistry, equipment, safety, customer performance or plant economics.

## Verification and Wheel delivery

![Verification pipeline](docs/assets/readme/verification-pipeline.svg)

```bash
python scripts/generate_readme_assets.py
python scripts/generate_extended_readme_assets.py
python scripts/generate_decision_readme_assets.py
python scripts/run_ci.py
python skills/epdm/scripts/audit_epdm.py
python skills/poe/scripts/audit_p0.py --root .
python skills/poe/scripts/audit_p1.py --root .
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse
python scripts/verify_wheel_runtime.py --wheel-dir wheelhouse
```

Wheel verification has two independent gates:

1. **content gate:** requires the executable core, complete four-Skill tree, contracts, schemas, reports, maintenance scripts, examples and all 16 diagrams;
2. **installation gate:** verifies `pip install --target` and a clean standard virtual environment with no inherited system site packages; every TSAO, EPDM and POE module plus the Skillpack data root must resolve inside the selected installation root before installed-README and known-solution checks may pass.

CI covers Ubuntu/Python 3.11–3.14 plus Windows and macOS on Python 3.14. It checks compilation, tests, branch coverage, contracts, provenance, Ruff, EPDM/POE audits, deterministic graphics, Wheel members, real installed runtime and CLI smoke. Independent post-coverage audits run concurrently, and Ubuntu/Python 3.14 enforces the versioned performance-regression gate.

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
