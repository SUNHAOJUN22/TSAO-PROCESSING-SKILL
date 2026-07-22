---
name: TSAO-PROCESS-GENERAL
version: 0.1.0-tsao.1
inherits: ../../SKILL.md
---

# General Chemical Process Development Subskill

## 1. Scope

Use this subskill for chemical-process projects not primarily governed by a polymer specialist: catalytic and non-catalytic reaction systems, petrochemicals, refining, fine and pharmaceutical chemicals, biochemical and fermentation processes, electrochemical systems, crystallization and solids processing, formulation, utilities, retrofit, debottlenecking, troubleshooting and third-party package review.

This is a process-development operating method, not a database of default conditions. All public and inherited parameters are screening inputs until project evidence qualifies them.

## 2. Mandatory causal chain

`product/service requirement → chemistry and reaction network → raw-material and impurity specification → analytical system → thermodynamics and transport → reactor and residence-time architecture → separation/recycle → utilities and heat integration → dynamic control and operability → HSE/reliability → pilot/scale-up → economics/environment → technology package → commissioning and field learning`

## 3. Route families

Evaluate applicable alternatives rather than selecting from familiarity:

- homogeneous, heterogeneous, enzymatic, electrochemical and photochemical reaction routes;
- batch, semi-batch, continuous stirred, plug-flow, loop, trickle-bed, slurry, packed-bed and membrane reactors;
- gas, liquid, solid, supercritical and multiphase regimes;
- distillation, absorption, extraction, adsorption, membrane, crystallization, precipitation, filtration, centrifugation, drying and reactive separation;
- conventional and intensified routes, including heat-integrated, membrane-reactor, reactive-distillation and continuous-manufacturing options.

Preserve at least one technically distinct counterfactual route until evidence closes the decision.

## 4. Required professional work

### 4.1 Chemistry and reaction basis

- define stoichiometry, reaction network, equilibrium, desired and undesired pathways;
- identify catalysts, reagents, inhibitors, poisons, corrosion precursors and impurity interactions;
- close mass, element, charge and, where relevant, biological or electrochemical balances;
- distinguish intrinsic kinetics from heat, mass-transfer and mixing limitations;
- quantify reaction heat, gas generation, accumulation, runaway and quench/termination behaviour.

### 4.2 Measurement and data

- qualify sampling, calibration, precision, bias, detection limit, time alignment and sample stability;
- maintain material, sample, method, dataset and instrument passports;
- reconcile plant and experiment data with gross-error detection rather than silently forcing closure;
- preserve raw data, transformations, exclusions, deviations and uncertainty.

### 4.3 Thermodynamics and physical properties

- select property methods by chemistry, pressure, polarity, association, electrolyte, polymer, solids and phase regime;
- validate VLE/LLE/SLE, density, enthalpy, heat capacity, viscosity, diffusivity and interfacial properties against independent data;
- state extrapolation, metastability, precipitation, fouling and critical-region limitations;
- use more than one method or tool for high-consequence predictions.

### 4.4 Reactor engineering

- compare reactor architectures using kinetics, residence-time distribution, mixing, transport, heat removal, catalyst handling, fouling and controllability;
- declare characteristic times and dimensionless groups;
- verify conservation, numerical convergence, sensitivity, identifiability and applicability domain;
- define start-up, shutdown, emergency quench, isolation and loss-of-utility responses.

### 4.5 Separation, recycle and finishing

- close the complete recycle network, including trace impurities, inerts, heavy/light by-products and purge;
- model non-ideal and non-equilibrium operations where justified;
- verify product losses, residuals, solvent/water/VOC closure, waste treatment and off-spec handling;
- evaluate energy integration without creating unsafe thermal coupling or loss of operability.

### 4.6 Control, safety and reliability

- derive dynamic models from a qualified steady and physical basis;
- establish controlled/manipulated/disturbance variables, constraints, alarms, interlocks and independent protection layers;
- provide HAZID/HAZOP/LOPA/SIL and relief-design handoffs without claiming completion;
- address materials compatibility, corrosion, erosion, fouling, plugging, catalyst ageing, rotating equipment and maintainability;
- quantify availability, critical spares, inspection and proof-test requirements.

### 4.7 Scale-up and industrialization

- separate laboratory chemistry proof, continuous-bench integration, pilot engineering learning, demonstration representativeness and industrial guarantee;
- state preserved physics, broken similarities and compensating experiments;
- use scale-down and transient tests to expose mixing, heat-transfer, mass-transfer, phase and control limitations;
- require independent validation before design-freeze or customer/plant qualification.

## 5. Domain-specific overlays

- **Bioprocess:** organism/enzymatic state, sterility, oxygen transfer, broth rheology, inhibition, contamination, downstream recovery and biosafety.
- **Electrochemical:** charge balance, current efficiency, electrode kinetics, ohmic loss, mass transport, gas evolution, thermal management and degradation.
- **Solids/crystallization:** supersaturation, nucleation/growth/agglomeration, polymorph, PSD, slurry rheology, filtration, drying, dust and electrostatics.
- **Fine-chemical batch:** dosing trajectory, accumulation, selectivity, heat-release timing, cleaning, campaign scheduling and recipe/version control.
- **Petrochemical/refining:** feed variability, catalyst deactivation, high-pressure/high-temperature integrity, fractionation, hydrogen/steam networks, flare and energy integration.

## 6. Fail-closed conditions

HOLD the relevant Gate when:

- chemistry or elemental/charge balance is unresolved;
- the property method is selected only by software default;
- kinetic parameters confound transport or are not independently identifiable;
- reaction calorimetry or credible heat-removal basis is absent for exothermic operation;
- recycle impurities and purge are not closed;
- a separation is idealized beyond its validated domain;
- start-up, shutdown, utility failure or relief basis is missing;
- scale-up uses capacity or geometry ratios without mechanism/time-scale evidence;
- customer, regulatory, safety or industrial approval is inferred from simulation or laboratory success.

## 7. Required outputs

Produce the master TSAO deliverables plus a reaction-basis dossier, property-method qualification, reactor-selection study, separation/recycle closure, utility and heat-integration basis, dynamic/operability study, HSE/reliability handoff, pilot and scale-up claim register, TEA/LCA inventory and process-package acceptance matrix.
