# Numerical audit — 2026-11-15

Base commit: `ed19bb1246efb631a4342640f83c90da47c690a3`. Only `main` was present in the coordinator's live GitHub inventory; this review created no remote branch.

## Corrections

1. **EPDM Arrhenius limits.** Equal actual/reference temperatures now preserve the reference rate exactly, including finite subnormal temperatures. Zero activation energy keeps a constant rate; the same identity now holds for the parameter bundle. Indeterminate or nonfinite derived exponents/results fail explicitly. Existing scalar conversion exception types remain unchanged.
2. **POE stoichiometric conservation.** Mass consistency now uses exact products and a relative residual. Scaling every stoichiometric coefficient and inversely scaling reaction extent cannot hide an inconsistent molecular-weight balance. Balanced reactions at extreme finite normalization still pass.

The tests reproduce the old failures and include valid as well as invalid cases. The 26 new regression cases cover both models. The source overlays were refreshed with the actual edited file hashes.

## Executed validation

- Full configured suite: **1,374 passed; 6 Windows-only tests skipped; no failed tests** (1,380 collected).
- Existing branch-coverage gate: **84% displayed**, above its 75% requirement.
- Capability, EPDM, POE P0/P1, source doctor and Ruff checks: passed.
- Exact hashed dependency-lock verification: passed (30 package records).
- EPDM software-acceptance fixture: passed all eight checks with seven loader samples.
- Skillpack, routing, process-package, EPDM/POE reference CLI and README visual checks: passed.
- `git diff --check`: passed before commit.

The complete `scripts/run_ci.py` process returns 1 here because its parallel `compileall -j 0` requires a forkserver Unix socket denied by the execution sandbox. The same source compilation ran successfully using `python -m compileall -q tsao scripts skills`. Every other runner stage passed. This is recorded as an environment block, not a complete native CI pass.

[validation.json](validation.json) records commands, return codes, baseline failures, tested content hashes and scope. This record describes local software verification. It does not assert scientific calibration, engineering acceptance or industrial performance. Authoritative GitHub CI supplies the remaining platform evidence.
