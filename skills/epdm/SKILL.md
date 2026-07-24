---
name: TSAO-EPDM
version: 9.1.0-tsao.2
inherits: ../../SKILL.md
---

# EPDM flagship process-package subskill

EPDM is TSAO's deepest specialist route. It inherits the universal process-package platform and adds active-site-normalized catalyst comparison, E/P/diene competition, molecular-architecture risk, long-chain branching, high-viscosity reactor constraints, recovery/recycle impurities and poison memory, compound/cure bridges and customer-line acceptance.

## Mandatory chain

`application/CQA → catalyst benchmark and active sites → E/P/diene insertion/transfer/deactivation → sequence/MWD/CCD/retained unsaturation/LCB/gel → phase stability/mixing/heat removal → quench/deashing/devolatilization/recycle → Mooney/compound/cure → durability/customer line → process package`

## Executable reference layer

- `skills.epdm.kinetics`: ternary insertion rates, active-site normalization and architecture metrics;
- `skills.epdm.process`: heat-removal margin, mixing, recycle poison, devolatilization, transition and Mooney references;
- `skills.epdm.qualification`: fail-closed EPDM case validator;
- `skills.epdm.package_audit`: universal process-package plus EPDM-specific audit;
- `skills/epdm/data/module_contracts.json`: fourteen machine-readable professional modules;
- `skills/epdm/data/requirements.json`: twenty explicit Gate requirements.

## Non-negotiable holds

HOLD when the vanadium benchmark is missing without approved retirement, active sites are not anchored, diene topology is unmeasured, heat/mixing/phase stability is open, recycle poison is unclosed, devolatilization lacks a non-equilibrium basis, or the chain from raw polymer to customer line is incomplete.

All historical catalyst experiments, licensed EOS/CFD, HAZOP/LOPA/SIL, equipment design, compounds and customer trials remain `NOT_EVALUATED` until executed and approved by named qualified teams.
