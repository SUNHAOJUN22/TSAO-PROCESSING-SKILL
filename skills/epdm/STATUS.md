# EPDM flagship status — alpha.11 / Phase A0 hardening

| Field | Status |
|---|---|
| subskill version | `9.1.0-tsao.2` |
| software implementation | `EXECUTABLE_FLAGSHIP_ALPHA_P1_REFERENCE` |
| V1 public API and golden numerics | `LOCKED` |
| malformed-input handling | `FAIL_CLOSED_WITH_INTERNAL_ERROR_SIGNAL` |
| parameter and scientific-declaration provenance | `REQUIRED` |
| package evidence existence | `REQUIRED` |
| package evidence status | `QUALIFIED_REQUIRED` |
| retracted or superseded EPDM evidence | `FAIL` |
| reported, calculated or HOLD EPDM evidence | `HOLD` |
| evidence applicability | `CHECKED_AT_PACKAGE_GATE` |
| variable-volume V1 semibatch active-site basis | `HOLD_FIXED_ACTIVE_SITE_CONCENTRATION` |
| scientific/engineering/HSE/customer/industrial approval | `NOT_EVALUATED` |

The V1 numerical kernel remains a software reference. A passing software audit does not grant
scientific, engineering, safety, customer or industrial approval. Current source-tree qualification
is authoritative only when bound to a named commit and a successful permanent CI run in
`reports/EPDM_PHASE_A0_QUALIFICATION.json`.
