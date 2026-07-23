---
name: TSAO-POE
version: 1.1.0-tsao.2
inherits: ../../SKILL.md
status: executable-specialist-alpha
scientific_execution: UNDER_DISTILLATION
process_package_qualification: CONTENT_LEVEL_SOFTWARE_AUDIT_ALPHA
---

# POE Solution-Polymerization Subskill

This subskill specializes TSAO for polyolefin-elastomer solution-polymerization research and process-package work. Alpha.6 retains the correct evidence → kinetics → properties → reactor → flowsheet → dynamics → scale-up → acceptance chain while making the current implementation depth explicit.

## Current qualification status

- technical chain: `IMPLEMENTED`;
- governance and fail-closed contract: `IMPLEMENTED`;
- audited historical-asset registry: `REGISTERED_139_OF_139`;
- POE scientific execution: `UNDER_DISTILLATION`;
- transparent kinetics/property/case kernels: `P0_REFERENCE_ONLY`;
- process-package audit: `CONTENT_LEVEL_SOFTWARE_AUDIT_ALPHA`;
- historical Aspen, MATLAB and Origin assets: `CONTROLLED_HISTORICAL_EVIDENCE`;
- scientific, engineering, HSE, customer and industrial approval: `NOT_EVALUATED`.

The open software layer is an `EXECUTABLE_SPECIALIST_ALPHA`; it is not stable, fully scientifically qualified or industrially validated.

## Mandatory technical chain

`target grade → catalyst/comonomer strategy → insertion and chain-transfer kinetics → polymer-solution thermodynamics/rheology → reactor residence time, mixing and heat removal → steady flowsheet and balances → recovery/recycle/purge → devolatilization/finishing → dynamic control and transitions → scale-up → content-level package acceptance`

## Twelve module contracts

1. `modules/01_product_cqa`
2. `modules/02_catalyst_impurity`
3. `modules/03_kinetics_network`
4. `modules/04_parameter_estimation`
5. `modules/05_thermodynamics_properties`
6. `modules/06_rheology_transport`
7. `modules/07_reactor_cfd_heat_removal`
8. `modules/08_steady_flowsheet_balances`
9. `modules/09_devolatilization_finishing`
10. `modules/10_recovery_recycle_purge`
11. `modules/11_dynamics_control_transitions`
12. `modules/12_scaleup_package_acceptance`

Every module declares inputs, SI units, equations/algorithm or external-execution contract, outputs, applicability, evidence mapping, failure modes and positive/boundary/malicious tests.

## Evidence registers

The source corpus is retained as **historical evidence** with controlled identity and no automatic design authority.


- `data/source_asset_registry.json` indexes twelve checked shards covering all 139 audited source assets and separates canonical, backup, history, snapshot, temporary, empty and unrelated items.
- `data/requirement_trace.json` links contract/requirement → criterion → source assets → verification → deviation → Gate → approval state.
- `data/conflict_ledger.json` retains solvent identity, scale-name, active-site, recycle, 200 kt/y dynamic-evidence, source-hygiene and unrelated-file conflicts.
- `docs/HISTORICAL_KINETICS_REVIEW.md` records why `POE_Kinetics.m` is not the trusted kernel.
- `fixtures/scientific_fixtures.json` contains synthetic/deidentified known-solution and failure fixtures, not historical setpoints.

## Executable P0 reference logic

`core.py` provides:

- an independent single-site copolymerization moment-model fixture;
- unit/non-negativity/mass-balance checks and Mn/Mw/composition outputs;
- property-method qualification for PC-SAFT, SRK, REFPROP, STEAMNBS and custom methods;
- simulator-neutral steady/dynamic case validation;
- asset, requirement and conflict audits;
- manifest-driven, content-level package auditing with Chinese/English legacy discovery.

These tools qualify software contracts and detect false PASS. They do not replace fitted kinetics, commercial simulation, experiments or engineering review.

## Non-negotiable HOLD conditions

HOLD when:

- component or solvent identity is unresolved;
- rate equations, units or parameter provenance are incomplete;
- a property method is missing, out of range or extrapolated without review;
- polymer viscosity invalidates mixing/heat-transfer assumptions;
- recycle connections, impurity memory or purge basis are absent;
- a dynamic claim lacks a matching model asset, initialization, volumes, controls and disturbances;
- the process package lacks manifest, evidence, content, cross-references, deviations or named approval;
- scale-up relies only on capacity or geometric ratios.

Structural inconsistency, unsafe paths, wrong hashes, placeholder deliverables and broken cross-references are `FAIL`, not HOLD.

## External execution boundary

Catalyst preparation, high-pressure polymerization, calorimetry, commercial Aspen/Origin/MATLAB execution, CFD, equipment/relief design, HAZOP/LOPA/SIL, pilot operation, permitting, customer qualification and industrial guarantees remain `NOT_EVALUATED` until performed and approved by named qualified teams.
