# EPDM Phase A4 / Alpha.15 numerical integration

Phase A4 adds an opt-in adaptive Dormand–Prince 5(4) integration layer above the locked Phase A3 structural RHS.

## Software contract

Every request records the parameter-bundle, rate-package, generated-state and reaction-network identifiers; time interval; step bounds; tolerances; maximum attempts; non-negative-state policy; conservation policy; applicability requirement; software qualification boundary; and scientific approval state.

The integrator:

- rejects invalid identifiers, booleans used as numerics, NaN/Infinity, reverse time, integer time coordinates that lose precision on conversion to floating-point, and invalid step/tolerance ranges;
- propagates Phase A3 HOLD/FAIL decisions without inventing default parameters;
- rejects and reduces steps that create negative intermediate or candidate states, clamping only round-off values within the declared tolerance;
- reports suspected stiffness, minimum-step exhaustion and maximum-step-count exhaustion as machine-readable HOLD states;
- applies `maximum_consecutive_rejections` to every rejected attempt, including negative intermediate stages; an accepted step resets this counter;
- records accepted/rejected attempts, monotonic times, embedded error estimates and explicit external-flow integrals;
- uses the actual representable time increment for every Runge–Kutta stage and its recorded step bounds; if the floating-point time coordinate cannot advance within the requested bounds, returns `A15_TIME_RESOLUTION_HOLD` before evaluating another RHS and preserves completed-step evidence;
- verifies named site inventories, total polymer-unit inventory and the Phase A3 E/P/D static conservation ledgers.

Large absolute time origins can make a small requested increment unrepresentable. The integrator rounds the proposed endpoint downward when necessary to stay within the proposed step, then uses that endpoint difference throughout the attempt. A final interval shorter than `minimum_step_s` remains permitted; ordinary relative round-off up to `1e-12` at the minimum bound is tolerated. A time-resolution HOLD can be addressed with a relative time origin or scientifically justified wider step bounds; it is not evidence of reaction stiffness.

## Boundary

The implementation uses synthetic calculated-reference parameters and is software verification only. It does not establish calibrated kinetics, GPC/PBM validity, reactor design, HSE approval, customer qualification or industrial performance.
