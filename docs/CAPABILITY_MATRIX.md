# TSAO capability matrix — 0.1.0-alpha.6

| Capability | Master | Process-general | EPDM | POE | Polymer-general | Verification |
|---|---:|---:|---:|---:|---:|---|
| G0–G18 Gate lifecycle | native | inherits | inherits | inherits | inherits | Gate Schema, sequence and false-PASS attacks |
| 14 workstreams / 266 packages | native | inherits | inherits | inherits | inherits | bootstrap, audit and work-package Schema |
| M0–M9 maturity | native | inherits | detailed | supported | detailed | maturity Schema and fail-closed tests |
| Evidence/claim/assurance graph | native | supported | detailed | supported | supported | evidence, source and graph contracts |
| Measurement and data qualification | native | detailed | detailed | detailed | supported | method/data tests and provenance audit |
| Thermodynamics/kinetics/reactors | framework | general kernels | EPDM-specific | POE-specific | mechanism-neutral | known solutions, invalid-input and domain tests |
| Separation/recycle/control | framework | detailed | detailed | detailed | supported | balance, recycle, devolatilization and dynamic tests |
| Scale-up/pilot/package/acceptance | native | detailed | detailed | detailed | detailed | scale-up, work-package, external-execution and acceptance Schemas |
| Source and release integrity | native | inherits | attack-tested | audited | audited | core/full manifests, checksums, SBOM, snapshot and cleanroom tests |
| Cross-platform packaging | native | inherits | inherits | inherits | inherits | Ubuntu 3.11/3.12, Windows 3.12 and macOS 3.12 CI |

`native`, `detailed`, `supported` and `framework` describe software depth—not real project approval. Every physical, engineering, safety, legal, customer and industrial decision remains `NOT_EVALUATED` until project evidence and named approval exist.
