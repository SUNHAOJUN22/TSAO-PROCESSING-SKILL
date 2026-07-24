# TSAO Process Intelligence OS

[![CI](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml/badge.svg)](https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL/actions/workflows/ci.yml)

**One operating system for evidence-driven process packages. EPDM is the flagship specialist; POE is the evidence-rich specialist.**

## Three executable entrances

```bash
python -m pip install -e .[dev]
python -m tsao.cli doctor --root . --profile core
python -m tsao.cli init --brief examples/generic-process/brief.yaml --out work/demo
python -m tsao.cli audit --root work/demo
python -m tsao.cli package template --family "continuous chemical process"
python -m tsao.cli epdm reference-demo
python -m tsao.cli poe reference-demo
```

| Entrance | What is executable now |
|---|---|
| `tsao package` | universal design-basis, stream/equipment, mass/energy, controls, HSE, evidence, acceptance and approval audit |
| `tsao epdm` | flagship E/P/diene active-site, architecture, gel, heat/mixing, recovery, product/customer bridge and package audit |
| `tsao poe` | P1 POE kinetics/properties/reactors/dynamics/scale-up plus 139-asset evidence lineage |

## EPDM flagship

EPDM contains fourteen machine-readable modules and twenty Gate requirements spanning catalyst benchmarks, active sites, ternary kinetics, MWD/CCD/sequence, retained unsaturation, branching/gel, high-viscosity reactor constraints, quench/deashing/devolatilization, recycle poisons, Mooney/compound/cure, transitions, durability, customer line and final process-package acceptance.

## Verify

```bash
python scripts/run_ci.py
python skills/epdm/scripts/audit_epdm.py
python skills/poe/scripts/audit_p0.py --root .
python skills/poe/scripts/audit_p1.py --root .
python -m pip wheel --no-deps --no-build-isolation . -w wheelhouse
python scripts/verify_wheel_contents.py --wheel-dir wheelhouse
python scripts/verify_wheel_runtime.py --wheel-dir wheelhouse
```

GitHub Actions runs Ubuntu/Python 3.11–3.12, Windows/Python 3.12 and macOS/Python 3.12. Software PASS is not scientific, engineering, HSE, customer or industrial approval; those remain `NOT_EVALUATED` until supported by active-project evidence and named qualified approval.

`main` is the sole authoritative branch.
