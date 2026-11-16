# Scientific reasonableness audit — 2026-11-16

Baseline: `9a157ed2f97cd1400ec7850246735a9121c86d80`. The coordinator verified that the live repository had only `main` and no open pull request. This review makes no new branch.

## Findings and corrections

### Calibration plans could consume their declared holdout

The baseline semantic validator returned `PASS` when the reference composition target and its dataset were both relabeled `HOLDOUT` but remained assigned to a `SINGLE_SITE_GLOBAL` fitting stage that varied `KP-E`. The existing split checks compared identities across declared dataset roles; they did not bind those roles to the actual stage consuming the target. An `INDEPENDENT_VALIDATION` stage could also vary parameters or reuse a calibration target while retaining its validation label.

`_validate_calibration_plans` now rejects validation/holdout targets in fitting stages, requires evaluation-role targets for independent validation, and rejects any varied parameter in that independent stage. The error uses the existing `DATA_LEAKAGE` reason code. Existing observation, experiment and experiment-group overlap checks remain active. A positive regression demonstrates that a distinct holdout target with a separate experiment group can validate a frozen parameter set. The input project is preserved.

This correction closes a false scientific-plan admission. It does not claim that the repository actually trained a model on these holdouts: the acceptance runner exercises a synthetic reference model, while the canonical loader provides typed structural loading and reference resolution. Scientific semantic acceptance remains the validator's separate responsibility.

### Regression R² depended on the target reference origin

For observed values `[0, 2, 4]` and constant predictions `[2, 2, 2]`, the correct R² is `0`. Adding a common, exactly representable `1e16` origin to both changed the baseline result to approximately `0.409966`, despite unchanged residual errors. Normalizing the raw targets before removing their origin lost relative variation and inflated apparent model quality.

`regression_error_metrics` now subtracts a common target origin before normalization. If that subtraction overflows for opposite extreme finite values, it retains a scaled subtraction path. Existing finite residual handling, MAE/RMSE, percentage-error policy and constant-target conventions are preserved. Eleven regression cases compare R² with an independent `Fraction` calculation across five origins, two prediction patterns and an opposite-signed extreme range. Percentage error intentionally remains reference-dependent; the correction does not assert translation invariance for MAPE.

## Additional paths reviewed

The review inspected POE moment kinetics, chain transfer/deactivation assumptions, bounded least-squares estimation, reactor formulas, EPDM reference Arrhenius kinetics, semi-batch mass/heat balances, source-to-model loading, model passports and the software-acceptance runner. The PFR/CSTR formulas remain explicitly first-order and isothermal. Moment propagation uses the documented chain-independent reference assumptions. The semi-batch thermal model uses a positive released-heat magnitude and simplified heat capacity/active-site assumptions. No unsupported plant-scale physics or sign convention was silently substituted.

## Validation

Against unchanged baseline source, the seventeen new scientific regressions produced **12 failed and 5 passed** assertions: four calibration-role failures and eight origin-dependent R² failures. After correction, all seventeen targeted cases passed. Both effective source overlays were refreshed with the actual edited file identities; baseline manifests remain preserved.

- Full configured suite: **1,391 passed; 6 Windows-only tests skipped; 0 failed** (1,397 collected).
- Existing branch-coverage gate: **84% displayed**, above its 75% requirement.
- Capability, EPDM, POE P0/P1, source doctor and Ruff checks: passed.
- Exact hashed dependency-lock contract: passed (30 package records). The installed dependency graph passed `uv pip check --python .venv/bin/python`; this cached uv environment has no `pip` module.
- Canonical EPDM software acceptance: all eight checks passed with seven loader samples. Skillpack, routing, model-suite and specialist reference CLI checks passed.
- README generators, accessibility, synchronization and visual fixed point: passed. Controlled public-source/public-wheel policy checks returned the expected block.

The complete `scripts/run_ci.py` process returns 1 locally because `compileall -j 0` requires a forkserver Unix socket denied by this execution environment. Serial compilation of the same source passed. Every other runner stage passed. This is an environment block, not a complete native CI pass; the parallel gate was left intact.

[validation.json](validation.json) records commands, return codes, exact test counts, tested source hashes and scope. Repository-wide historical runtime-performance comparison was not rerun locally; exact-head CI retains that gate.

## Scientific limits and sources

This audit verifies software contracts and reference-model arithmetic. It does not establish experimental calibration, engineering approval, a plant design envelope, or industrial performance. The data-role guard relies on truthful dataset provenance: it cannot discover undisclosed reuse or relabeling outside the project evidence. Local validation uses Python 3.12; Windows and the wider Python matrix require exact-head CI. No paid service or remote scientific job was executed.

Method definitions were checked against primary documentation:

- [scikit-learn: R² coefficient of determination](https://scikit-learn.org/stable/modules/model_evaluation.html#r2-score-the-coefficient-of-determination).
- [scikit-learn: data leakage and separation of training/test data](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).
