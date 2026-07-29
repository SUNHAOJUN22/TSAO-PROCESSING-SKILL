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

## Phase A0 safety contracts

- V1 kinetic parameters must declare `parameter_basis` and non-empty `parameter_evidence_ids`; missing provenance returns `HOLD`.
- `SYNTHETIC_REFERENCE_TEST` parameters are accepted only when the case itself is declared as a software fixture. This does not grant scientific or engineering approval.
- Variable-volume V1 semibatch calculations retain the inherited fixed-active-site-concentration assumption so the public API and golden numerics remain unchanged. This behavior is locked as `CALCULATED_REFERENCE_ONLY`, cannot qualify engineering use, and must be replaced by an extensive active-site balance in V2.
- The V1 public API and selected numerical outputs are locked by machine-readable contract and golden-output fixtures.

## Non-negotiable holds

HOLD when the vanadium benchmark is missing without approved retirement, active sites are not anchored, diene topology is unmeasured, parameter provenance is absent, heat/mixing/phase stability is open, recycle poison is unclosed, devolatilization lacks a non-equilibrium basis, or the chain from raw polymer to customer line is incomplete.

All historical catalyst experiments, licensed EOS/CFD, HAZOP/LOPA/SIL, equipment design, compounds and customer trials remain `NOT_EVALUATED` until executed and approved by named qualified teams.
