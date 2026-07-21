# TSAO Architecture

TSAO is a contract-driven skill system, not a monolithic prompt.

## Layers

1. **Interaction layer** — project brief, user decisions and explicit approval points.
2. **Research layer** — planner/executor/publisher orchestration, evidence ledger, standards and IP mapping.
3. **Science layer** — chemistry, thermodynamics, kinetics, transport, population balances and data reconciliation.
4. **Process layer** — route synthesis, reactors, separation/recycle, utilities, dynamic control and operability.
5. **Scale layer** — lab, continuous bench, pilot, demonstration and industrial representativeness.
6. **Assurance layer** — typed assurance graph, model risk, Gate state machine, change propagation and independent review.
7. **Delivery layer** — process package, commissioning, qualification, transfer and field feedback.
8. **Software supply-chain layer** — schemas, tests, manifests, SBOM, deterministic archive and cleanroom validation.

## Typed digital thread

`requirement → claim → source → hypothesis → experiment → sample → method → dataset → model → parameter → design → equipment/control/barrier → test → gate → change → release → field evidence`

A high-consequence claim must have a continuous support path. Orphaned nodes, expired evidence, unresolved contradictions or unreviewed MR4/MR5 models block the relevant Gate.

## Plugin model

A specialist skill provides domain ontology, decision logic, models, templates and tests. It may narrow the master rules but may not weaken traceability, fail-closed Gates or approval boundaries.

## Simulator neutrality

The canonical project model is stored in TSAO schemas. DWSIM, IDAES, Cantera, Pyomo, CoolProp, Aspen and other tools are adapters. This prevents a project from becoming inseparable from one vendor file and makes cross-tool verification possible.

## Qualification boundary

Repository CI qualifies code and data contracts only. Scientific validity, engineering design, process safety, FTO, customer approval and industrial performance remain `NOT_EVALUATED` until real evidence and named accountable reviewers are present.