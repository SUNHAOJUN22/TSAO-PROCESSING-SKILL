---
name: TSAO-POE
version: 1.0.0-tsao.1
inherits: ../../SKILL.md
---

# POE Solution-Polymerization Subskill

This subskill specializes TSAO for polyolefin elastomer solution-polymerization technology packages. It distils the SJTU POE acceptance corpus into a reusable method without treating its historical parameters as universal setpoints.

## Mandatory technical chain

`target grade → catalyst/comonomer strategy → insertion and chain-transfer kinetics → polymer-solution thermodynamics → reactor residence-time and heat removal → steady flowsheet → solvent/monomer recovery → devolatilization and finishing → dynamic control → scale-up → acceptance package`

## Required workstreams

- catalyst, activator, scavenger and impurity-tolerance comparison;
- ethylene/comonomer incorporation, molecular-weight and comonomer-distribution kinetics;
- high-pressure phase equilibrium, polymer-solution viscosity and heat-capacity qualification;
- CSTR/PFR/series-reactor model selection and identifiability;
- mass, element, energy, solvent, impurity, VOC and water closure;
- flash, separation, recycle purification, steam stripping or alternative devolatilization;
- steady-state simulation plus independent balance checks;
- dynamic disturbances, grade transitions, soft sensing and control design;
- lab, continuous bench, pilot and industrial similarity claims;
- equipment, utilities, safeguards, TEA, environmental inventory and acceptance matrix.

## Evidence boundary

SJTU report data, Aspen files, MATLAB kinetics, Origin results and scale-up examples are historical evidence. Before reuse, the active project must verify chemical identity, units, measurement boundary, property method, catalyst batch, reactor geometry, recycle impurity state and operating envelope.

## Fail-closed conditions

HOLD when the property method is not qualified, the kinetic model cannot predict independent batches, polymer viscosity invalidates mixing/heat-transfer assumptions, recycle impurities are missing, devolatilization is represented as equilibrium only without justification, or scale-up relies solely on geometric ratios.
