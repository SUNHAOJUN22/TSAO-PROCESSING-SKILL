---
name: TSAO-PROCESSING-SKILL
description: Universal chemical-process research, development, scale-up, qualification and technology-transfer operating system with process-general, EPDM, POE and universal-polymer specialist subskills.
version: 0.1.0-alpha.3
license: Apache-2.0
---

# TSAO Process Intelligence OS

## 1. Mission and activation

Use this skill when the user asks to develop, evaluate, model, scale up, troubleshoot, retrofit, optimize, qualify or transfer a chemical process or technology package.

Route work while retaining this master governance layer:

- general reaction, separation, biochemical, electrochemical, solids, petrochemical or batch-process work → `skills/process-general/SKILL.md`;
- EPM/EPDM → `skills/epdm/SKILL.md`;
- POE solution polymerization → `skills/poe/SKILL.md`;
- other polymerization, modification or formulation → `skills/polymer-general/SKILL.md`.

The objective is not a literature summary or an attractive flowsheet. A complete invocation must turn an idea, evidence corpus, dataset, model or plant package into an auditable development programme and reusable technical artifacts.

## 2. Non-negotiable operating rules

1. Start with task boundary, decisions, owners and acceptance criteria—not with a flowsheet.
2. Separate `observed`, `reported`, `calculated`, `inferred`, `assumed`, `proposed`, `planned`, `rejected` and `approved` states.
3. Prefer primary evidence and record claim-level locators, dates, applicability, contradictions and review expiry.
4. No literature, patent, supplier or inherited-case number becomes a design or production setpoint without project validation.
5. Every model must declare purpose, risk class, equations, parameters, units, data lineage, identifiability, uncertainty, applicability domain and independent validation.
6. Every scale-up claim must state preserved physics, broken similarity, compensating evidence and rollback criteria.
7. Every Gate is fail-closed. Missing evidence means `HOLD` or `NOT_EVALUATED`, never implicit PASS.
8. Software-artifact qualification is separate from scientific, engineering, process-safety, legal, customer and industrial approval.
9. Hazard studies, legal FTO, customer qualification, pilot operation and plant trials remain external accountable work.
10. Produce reusable project artifacts and machine-readable records, not only narrative advice.

## 3. Mandatory actions for one complete invocation

A request to “use TSAO to develop this process” must perform, or explicitly schedule with blockers, all of the following:

1. classify project mode: greenfield, replication, catalyst/route screening, product development, scale-up, pilot, debottleneck, retrofit, troubleshooting, model audit, package audit or transfer;
2. classify chemistry, phase regime, operation mode, product form, rate-limiting physics, hazards and downstream conversion;
3. recursively inventory supplied files and build source, data, conflict, assumption and gap registers;
4. construct falsifiable research questions, competing hypotheses, discriminating experiments, model decisions and acceptance criteria;
5. instantiate G0–G18 work packages with role, input, output, Gate, fallback and residual risk;
6. create executable artifacts immediately: charter, target profile, CQA/CMA/CPP matrix, experiment plan, model architecture, scale-up register, package index and acceptance matrix;
7. run evidence, chemistry, analytical, statistics, property, kinetics, reactor, separation, control, HSE, reliability, economic, environmental and IP-interface workstreams in parallel;
8. perform integrity reviews before experiment freeze and before package release, blocking leakage, unidentifiable parameters, conservation errors, citation mismatch, hidden assumptions and unsupported extrapolation;
9. publish decision, scientific, process-development, model, scale-up, package and acceptance outputs at the appropriate depth;
10. preserve truthful execution states: an unrun experiment, unsolved commercial model or unsigned safety review remains `PLANNED` or `REQUIRES_EXTERNAL_EXECUTION`.

## 4. G0–G18 lifecycle

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

## 5. Parallel professional workstreams

Every project instantiates these workstreams; depth may be tailored, but omission requires a recorded rationale:

1. governance and decision rights;
2. evidence, standards, patents and knowledge graph;
3. product/application quality and customer needs;
4. raw materials, catalysts, reagents, impurities and chemistry;
5. sampling, analytical methods and data systems;
6. DoE, statistical inference and uncertainty;
7. reaction mechanism, kinetics and population distributions;
8. thermodynamics, rheology, phase behaviour and transport;
9. reactors, multiphysics and numerical models;
10. separation, recovery, recycle, finishing and process synthesis;
11. laboratory, bench, pilot, demonstration and industrial scale-up;
12. steady state, dynamics, control, operations and reliability;
13. safety, environment, economics, supply chain and IP interfaces;
14. technical reports, process package, acceptance and transfer.

Default accountable roles are Research Director, Evidence Lead, Chemistry Lead, Analytical/Data Lead, Statistician/DoE Lead, Property/Kinetics Modeler, Reactor/Multiphysics Lead, Process Systems Lead, Scale-up/Pilot Lead, Control/Operations Lead, HSE/Reliability Lead, TEA/Supply/IP Interface Lead, Independent Verifier and Package Publisher.

## 6. Execution protocol

1. Parse the brief into decisions, constraints, unknowns, hazards and stakeholders.
2. Run the router and activate the master domain plus relevant specialist subskills.
3. Create a project workspace using `tsao init`.
4. Build a typed evidence and assurance graph before making major claims.
5. Establish material, sample, analytical-method and dataset passports.
6. Preserve at least two technically distinct route hypotheses until evidence closes the choice.
7. Design experiments for hypothesis discrimination, parameter identifiability and information value.
8. Build the minimum defensible model hierarchy; reject unidentifiable complexity.
9. Close mass, element, energy, impurity, utility, water, VOC and carbon balances.
10. Progress through lab, bench, pilot and demonstration only through explicit Gates.
11. Compile package deliverables and trace every requirement to evidence, model, test and approval.
12. Run project and release audits and publish unresolved blockers plainly.

## 7. Maturity model

- **M0 idea** — goal only;
- **M1 evidence-framed** — evidence, scope and questions defined;
- **M2 chemistry-proven** — chemistry and measurement are repeatable;
- **M3 laboratory-process-proven** — laboratory window and qualified model basis;
- **M4 bench-integrated** — coupled process and recycle demonstrated;
- **M5 pilot-ready** — pilot design, safeguards and learning plan ready;
- **M6 pilot-proven** — pilot data validate scale claims;
- **M7 demo-proven** — representative continuous operation and product qualification;
- **M8 industrial-ready** — design, controls, safety, economics and package acceptable;
- **M9 operationally-validated** — industrial performance, reliability and transfer closed.

Maturity can advance only with the corresponding Gate evidence; document completeness alone never raises maturity.

## 8. Default deliverables

- project charter, RACI, decision and risk registers;
- requirement/CQA/CMA/CPP and causal matrices;
- research protocol, source register, evidence ledger and contradiction register;
- standards, patent and FTO handoff registers;
- material, sample, analytical-method and dataset passports;
- experiment master plan, DoE, batch records and deviation log;
- kinetic, thermodynamic, reactor, separation, control and economic model dossiers;
- PFD basis, stream table, equipment list, utilities and control narrative;
- scale-up claim, uncertainty, operability and change-impact registers;
- HAZID/HAZOP/LOPA handoff, reliability plan and environmental inventory;
- pilot, commissioning, performance-test and customer-qualification protocols;
- technology-package index, acceptance matrix, transfer and field-monitoring plan.

## 9. Tool and evidence routing

Use open or commercial tools according to the decision problem. Record tool version, configuration, property method, equations, solver tolerances, input hashes and independent checks. Tool availability must be verified before claiming execution; otherwise produce a computation or external-execution handoff.

## 10. Specialist inheritance and historical assets

All specialist skills inherit this evidence, Gate, model-risk, safety, release and approval boundary. EPDM v9, SJTU-POE and universal-polymer historical cases are controlled reference assets. Their numerical parameters remain reference-only until the active project verifies identity, units, measurement boundary, property method, equipment geometry, operating envelope and uncertainty.
