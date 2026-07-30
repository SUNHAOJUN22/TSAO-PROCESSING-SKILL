---
name: TSAO-EPDM
version: 9.1.0-tsao.2
inherits: ../../SKILL.md
---

# EPDM flagship process-package subskill

EPDM is TSAO's deepest specialist route. It inherits the universal process-package platform and adds active-site-normalized catalyst comparison, E/P/diene competition, molecular-architecture risk, long-chain branching, high-viscosity reactor constraints, recovery/recycle impurities and poison memory, compound/cure bridges and customer-line acceptance.

## Mandatory chain

`application/CQA → catalyst benchmark and active sites → E/P/diene insertion/transfer/deactivation → sequence/MWD/CCD/retained unsaturation/LCB/gel → phase stability/mixing/heat removal → quench/deashing/devolatilization/recycle → Mooney/compound/cure → durability/customer line → process package`

## Three model levels

1. **Screening:** active-site-normalized ternary insertion, transfer and deactivation with rapid pseudo-first-order conversion estimates.
2. **Engineering:** Arrhenius temperature correction, residence-time conversion, heat-removal margin, mixing Reynolds number, recycle-poison closure, devolatilization Damköhler number and semibatch material/energy steps.
3. **Detailed reference:** heterogeneous active-site families, chain-moment/dispersity references, branch/gel risk, Flory–Huggins spinodal margin and irreversible heat-transfer entropy generation.

Every numerical layer is explicitly labelled `CALCULATED_REFERENCE_ONLY` until parameters are fitted to a named dataset and approved. The detailed reference layer is not a replacement for a qualified population balance, CFD model, EOS package or plant historian.

## Executable reference layer

- `skills.epdm.kinetics`: ternary insertion rates, active-site normalization, Arrhenius scaling, three-level kinetics and architecture metrics;
- `skills.epdm.process`: conservative semibatch material/energy stepping, heat removal, mixing, phase stability, recycle poison, devolatilization, transition and Mooney references;
- `skills.epdm.qualification`: fail-closed EPDM case validator;
- `skills.epdm.package_audit`: universal process-package plus EPDM-specific audit;
- `skills/epdm/data/module_contracts.json`: fourteen machine-readable professional modules;
- `skills/epdm/data/requirements.json`: twenty explicit Gate requirements;
- `python -m tsao.cli epdm model-suite`: executable multi-level reference demonstration.

## Phase A0 governed evidence and assumption contracts

- Every kinetic parameter basis and every scientific declaration used to clear a Gate must carry non-empty, unique evidence IDs.
- Package-level evidence resolution requires `QUALIFIED` status, a locator and an applicability statement. `RETRACTED` or `SUPERSEDED` evidence is a hard `FAIL`; `REPORTED`, `CALCULATED` or `HOLD` evidence keeps the package on `HOLD`.
- Synthetic fixtures may only use evidence whose applicability explicitly covers software, fixture or synthetic reference testing. Project cases cannot be qualified by synthetic-only evidence.
- Variable-volume V1 semibatch calculations preserve the locked numerical and return contract. A governed `SEMIBATCH` case using `FIXED_CONCENTRATION_REFERENCE` is placed on `HOLD`; V2 must replace this with an extensive active-site balance.
- Expected malformed payloads return specific validation errors with `internal_error=false`. The defensive public boundary marks unexpected programming failures with `internal_error=true`, so tests cannot treat hidden exceptions as normal validation success.
- V1 public names, selected function signatures, return envelopes and golden numerical outputs are machine-locked.

## Non-negotiable holds

HOLD when the vanadium benchmark is missing without approved retirement, active sites are not anchored, diene topology is unmeasured, parameter provenance is absent, heat/mixing/phase stability is open, recycle poison is unclosed, devolatilization lacks a non-equilibrium basis, or the chain from raw polymer to customer line is incomplete.

All historical catalyst experiments, licensed EOS/CFD, HAZOP/LOPA/SIL, equipment design, compounds and customer trials remain `NOT_EVALUATED` until executed and approved by named qualified teams.

## Phase A1 — V2 scientific contracts and schemas

- `contracts.py`, `registry.py`, `validation_v2.py`, `qualification_v2.py`, and `migration.py` are implemented as a contract-only opt-in layer.
- Stable V2 schemas reject unknown fields outside `extensions`; semantic validation resolves IDs, units, evidence states, applicability, dataset leakage, parameter binding, and state-basis consistency.
- The V1 migration adapter is metadata-only and never fabricates evidence or invokes unfinished V2 calculations.
- No V2 kinetic, thermodynamic, calibration, GPC, moment, reactor, or dynamic numerical result is claimed in Phase A1.
