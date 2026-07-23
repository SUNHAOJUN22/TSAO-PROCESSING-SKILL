# TSAO capability matrix — 0.1.0-alpha.7

| Capability | Master | Process-general | EPDM | POE | Polymer-general | Verification |
|---|---:|---:|---:|---:|---:|---|
| G0–G18 lifecycle | native | inherits | inherits | inherits | inherits | Gate Schema and false-PASS tests |
| 14 workstreams / 266 packages | native | inherits | inherits | inherits | inherits | bootstrap and work-package Schema |
| Evidence and lineage | native | supported | detailed | executable alpha | supported | 139 assets, 18 requirements, 7 conflicts |
| Kinetics and estimation | framework | general kernels | EPDM-specific | P1 reference | mechanism-neutral | conservation, bounded fit, Jacobian and identifiability |
| Properties and transport | framework | general kernels | EPDM-specific | P1 reference | supported | error metrics, ranges, viscosity and heat-transfer checks |
| Reactors and heat removal | framework | detailed | detailed | P1 reference | supported | PFR/CSTR known solutions and margin Gates |
| Steady/dynamic process cases | framework | detailed | detailed | executable validator | supported | component balances, convergence and dynamic assets |
| Dynamics and transitions | framework | detailed | detailed | P1 reference | supported | FOPDT, response metrics and recycle memory |
| Scale-up | native | detailed | detailed | P1 reference | detailed | dimensionless groups and similarity tolerances |
| Package and acceptance | native | detailed | detailed | audit v2 alpha | detailed | hashes, evidence, conflicts, requirements and approval |
| Model-asset passports | framework | supported | controlled | executable Schema | controlled | software/database/property/dependency identity |
| Wheel delivery | native | inherits | controlled | runtime verified | controlled | member and installed-runtime checks |
| Cross-platform packaging | native | inherits | inherits | qualified alpha | inherits | Ubuntu 3.11/3.12, Windows 3.12, macOS 3.12 |

These labels describe open-software depth, not project approval. Historical model execution and every scientific, engineering, HSE, legal, customer and industrial decision remain `NOT_EVALUATED` until supported by project evidence and named approval.
