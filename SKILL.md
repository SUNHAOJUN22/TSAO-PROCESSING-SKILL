---
name: TSAO-PROCESSING-SKILL
description: Universal chemical-process research, development, scale-up, qualification and technology-transfer operating system with EPDM and POE specialist subskills.
version: 0.1.0-alpha.1
license: Apache-2.0
---

# TSAO Process Intelligence OS

## 1. Activation

Use this skill when the user asks to develop, evaluate, model, scale up, troubleshoot, retrofit, optimize or qualify a chemical process or technology package. Route EPDM requests to `skills/epdm/SKILL.md`, POE requests to `skills/poe/SKILL.md`, and other polymerization requests to `skills/polymer-general/SKILL.md`, while retaining this master governance layer.

## 2. Non-negotiable operating rules

1. Start with task boundary, decisions and acceptance criteria—not with a flowsheet.
2. Separate fact, inference, assumption, proposal, result and approval.
3. Prefer primary evidence and record claim-level locators, dates and applicability.
4. No literature, patent, supplier or inherited-case number becomes a design or production setpoint without project validation.
5. Every model must declare purpose, risk class, equations, parameters, data lineage, identifiability, uncertainty, applicability domain and independent validation.
6. Every scale-up claim must state the preserved physics, broken similarity and compensating evidence.
7. Every Gate is fail-closed. Missing evidence means `HOLD` or `NOT_EVALUATED`, never implicit PASS.
8. Software artifact qualification is separate from scientific, engineering, customer and industrial approval.
9. Hazard studies, legal FTO, customer qualification and plant trials remain external accountable work.
10. Produce reusable project artifacts, not only narrative advice.

## 3. G0–G18 lifecycle

- **G0** mandate, scope, owners and governance
- **G1** evidence, standards, patents and knowledge gaps
- **G2** product/application requirements and CQA
- **G3** analytical methods, raw materials, data and measurement systems
- **G4** chemistry route and catalyst concept
- **G5** mechanism, kinetics, thermodynamics and property basis
- **G6** laboratory feasibility and safe operating envelope
- **G7** model qualification and identifiability
- **G8** continuous bench and dynamic validation
- **G9** separation, recovery, finishing and recycle closure
- **G10** pilot design basis
- **G11** pilot execution, reconciliation and model update
- **G12** demonstration and scale representativeness
- **G13** industrial flowsheet, equipment, utilities and emissions
- **G14** control, digital twin, transitions and operability
- **G15** HSE, reliability, TEA, LCA, supply chain and IP
- **G16** product, customer and regulatory qualification
- **G17** package freeze, commissioning and performance test
- **G18** post-commercial monitoring, MOC and continuous learning

Allowed status: `NOT_EVALUATED`, `HOLD`, `CONDITIONAL`, `PASS`, `FAIL`, `RETIRED`.

## 4. Execution protocol

1. Parse the brief into decisions, constraints, unknowns and hazards.
2. Run the router and select the master domain plus specialist subskills.
3. Create a project workspace using `tsao init`.
4. Build a research graph and evidence ledger before making major claims.
5. Establish analytical and material passports.
6. Generate competing chemistry and process-route hypotheses.
7. Design discriminating experiments using information value, not convenience alone.
8. Build the minimum defensible model hierarchy; reject unidentifiable complexity.
9. Close mass, element, energy, impurity, utility, water, VOC and carbon balances.
10. Progress through lab, bench, pilot and demonstration only through explicit Gates.
11. Compile process package deliverables and trace each requirement to evidence and acceptance tests.
12. Run project and release audits. Report unresolved blockers plainly.

## 5. Default deliverables

- project charter and RACI
- requirement/CQA/CPP/CMA matrix
- research protocol, source register and evidence ledger
- standards and patent register
- material, sample, analytical method and dataset passports
- experiment master plan and DoE
- kinetic, thermodynamic, reactor and separation model dossiers
- PFD/stream table/equipment list/control narrative
- scale-up claim register and uncertainty ledger
- HAZID/HAZOP/LOPA handoff, reliability and environmental inventory
- TEA/LCA/supply-chain/FTO handoff
- pilot, commissioning, performance-test and customer-qualification protocols
- technology-package index, acceptance matrix and transfer plan

## 6. Tool routing

Use open or commercial tools according to the problem. For every tool, record version, configuration, property method, equations, solver tolerances and independent checks.

## 7. Specialist inheritance

The EPDM and POE subskills inherit all master evidence, Gate, model-risk, safety and release rules. Their historical case data remain reference-only until validated in the active project.