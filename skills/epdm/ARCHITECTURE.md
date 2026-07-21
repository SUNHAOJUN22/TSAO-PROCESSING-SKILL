# EPDM subskill architecture

The EPDM subskill extends the TSAO mother lifecycle without changing its Gate semantics. It supplies domain-specific chemistry, data contracts, models and acceptance logic for EPM/EPDM development.

## Technical spine

```text
application QFD
→ ethylene/propylene/diene architecture target
→ catalyst-platform hypotheses
→ active-site formation and poisoning
→ ternary insertion/transfer/deactivation kinetics
→ MWD/CCD/sequence/LCB/gel topology
→ solution/slurry/gas-phase route screening
→ reactor heat, mixing, stability and observability
→ quench/deashing/flash/steam stripping/recycle purification
→ raw-polymer rheology and Mooney
→ fixed compound and cure response
→ part durability and customer-line qualification
→ industrial technology package and continuing verification
```

## Catalyst and monomer platforms

The router maintains, at minimum, a traditional vanadium industrial benchmark and one single-site/metallocene path. Post-metallocene or supported alternatives remain hypotheses until evidence supports them. ENB, DCPD, VNB and other diene choices are represented separately because insertion, retained unsaturation, branching, gel risk, cure response and recycle-memory behaviour differ.

## Mandatory model layers

- total-metal and active-site-normalized activity;
- E/P/diene terminal or higher-order insertion model;
- activation, dormancy, rapid/slow deactivation and impurity poisoning;
- hydrogen, monomer, aluminium, solvent and beta-hydride chain transfer;
- MWD and CCD population balances or qualified reduced-order equivalents;
- long-chain branching, second insertion and gel/percolation risk;
- polymer-solution phase stability and high-viscosity transport;
- non-equilibrium devolatilization coupling particle diffusion with residence-time distribution;
- recycle impurity accumulation, guard-bed breakthrough and purge optimization;
- Mooney/rheology/cure/compound/part causal bridge;
- grade-transition dynamics and off-spec material accounting.

## Fail-closed decisions

A route cannot pass a Gate merely because conversion or catalyst productivity is high. It must also satisfy composition control, molecular-architecture reproducibility, residual-metal/volatile limits, gel and filterability, heat-removal margin, analytical capability, customer-property bridge and HSE constraints. MR4–MR5 models require independent review and evidence outside the fitting dataset.

## External execution boundary

Catalyst synthesis, pyrophoric-material handling, high-pressure E/P/diene polymerization, reaction calorimetry, relief design, commercial EOS/CFD, HAZOP/LOPA/SIL, FTO, customer production-line trials and industrial performance guarantees remain `NOT_EVALUATED` until completed by qualified organizations.
