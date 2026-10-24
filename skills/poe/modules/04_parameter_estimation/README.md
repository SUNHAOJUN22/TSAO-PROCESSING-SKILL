# 04_parameter_estimation — Parameter estimation

## Purpose

Estimate identifiable kinetic/property parameters with uncertainty and independent validation.

## Evidence and lineage

Inputs must cite POE asset IDs from `../../data/source_asset_registry.json`, requirement IDs from `../../data/requirement_trace.json`, and open deviations from `../../data/conflict_ledger.json`. Historical Aspen, MATLAB and Origin files remain `CONTROLLED_HISTORICAL_EVIDENCE`; they are not redistributed or silently treated as qualified code.

## Input contract

datasets, model equations, priors/bounds, measurement uncertainty. Inputs use SI units unless a field explicitly declares and converts another unit. `contract.schema.json` defines the machine-readable input and output envelope.

## Equations or algorithm

Use the minimum model that can answer the decision. State equations, conservation basis, parameters, units, numerical tolerances, applicability domain and uncertainty. Module-specific executable reference logic is implemented in `../../core.py` where available; commercial simulation and physical experiments remain external.

## Output contract

parameter estimates, covariance/profile likelihood, residuals and applicability. Every output carries `status`, evidence IDs, applicability, uncertainty, blockers and approval state.

## Applicability domain

The module applies only to ethylene/alpha-olefin solution-polymerization cases whose component identities, measurement boundaries, property method, catalyst basis, scale and recycle state are explicitly declared.

## Fail-closed conditions

HOLD for non-identifiability, hidden hard-coding, missing units or validation leakage. Missing evidence returns `NOT_EVALUATED` or `HOLD`; structural inconsistency returns `FAIL`. No missing item is converted into an assumed PASS.

## Tests

Positive, boundary and malicious-input tests are located in `../../tests/test_poe_alpha6_p0.py` and `../../tests/test_poe_alpha6_package.py`. Required Gate: `G7`.

## External execution boundary

Physical polymerization, commercial Aspen/Origin/MATLAB execution, CFD, equipment design, HAZOP/LOPA/SIL, pilot operation, customer qualification and industrial guarantees remain `NOT_EVALUATED` until performed and approved by named qualified teams.

## Alpha.7 executable reference

`fit_first_order_rate` fits `X(t;k)=1-exp(-k t)` with time in seconds, rate in s⁻¹, and dimensionless conversion. A bounded golden-section candidate is followed by an immediate `J>=0` gap check; when it closes the requested gap, the fit is certified without interval splits. Otherwise, interval branch-and-bound is used. For interval `[a,b]`, monotonic predictions bound each `X(t_i;k)` between `X(t_i;a)` and `X(t_i;b)`; the weighted squared distance from each observation to that interval is a lower bound on the objective. A Taylor lower bound tightens the interval estimate when numerically usable. The fit reports `optimization_converged`, `global_objective_lower_bound_fraction`, `global_objective_gap_fraction`, `global_objective_tolerance_fraction`, and used/budgeted interval splits. The default objective-gap tolerance is `1e-12` of total weight and the default budget is 96 splits. If that gap is not closed before the budget expires, `status` is `HOLD`; `rate_constant_s` then remains only the best feasible candidate found. Floating-point pads are conservative working enclosures under binary64/libm assumptions, not formal real-arithmetic certification. SciPy likewise documents bounded scalar minimizers as local methods and points to global optimization for objectives with multiple minima: <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize_scalar.html>.

The separate `information_scalar`/`identifiable` pair is a local sensitivity threshold check and does not imply optimizer convergence. If its value is outside finite-float range, the scalar and identifiability result are `null`, keeping the overall status at `HOLD`. Scientific, engineering, HSE, customer and industrial approval remain `NOT_EVALUATED`.

`finite_difference_jacobian` retains its historical unit-scale step when `parameter_scales` is omitted. For small or dimensioned SI parameters, callers should pass one finite, positive characteristic scale per parameter; the central-difference step is then `relative_step * max(abs(parameter), parameter_scale)`. Select scales and operating points so both perturbations remain inside the model's valid domain. The routine does not infer units, bounds or a physically meaningful scale. It is a transparent reference, not an approved parameter-release system.
