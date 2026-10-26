from __future__ import annotations

import heapq
import math
from collections.abc import Callable, Sequence
from numbers import Real
from typing import Any

import numpy as np

_FLOAT_DTYPE = np.dtype(float)


def _finite_scalar(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{label} must be a finite real number; Boolean is rejected")
    try:
        number = float(value)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be a finite real number") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be a finite real number")
    return number


def _finite_vector(values: Sequence[float], label: str) -> np.ndarray:
    # Exact ndarrays preserve shape during dtype conversion; subclasses can
    # override shape metadata and must also be checked after normalization.
    if isinstance(values, np.ndarray):
        if values.ndim != 1 or values.size == 0:
            raise ValueError(f"{label} must be a non-empty finite one-dimensional sequence")
        kind = values.dtype.kind
        if kind not in "iuf":
            if kind == "b":
                _finite_scalar(values[0], f"{label}[0]")
            raise ValueError(f"{label} must be a non-empty finite one-dimensional sequence")
        array = np.asarray(values, dtype=float)
        if type(values) is not np.ndarray and (array.ndim != 1 or array.size == 0):
            raise ValueError(f"{label} must be a non-empty finite one-dimensional sequence")
    else:
        error = f"{label} must be a non-empty finite one-dimensional sequence"
        try:
            raw_values = tuple(values)
        except TypeError as exc:
            raise ValueError(error) from exc
        if not raw_values:
            raise ValueError(error)
        for index, value in enumerate(raw_values):
            # Exact builtins already satisfy Real; subclasses retain strict checks.
            if type(value) in (float, int):
                continue
            if isinstance(value, bool):
                _finite_scalar(value, f"{label}[{index}]")
            if not isinstance(value, Real):
                raise ValueError(error)
        try:
            array = np.asarray(raw_values, dtype=float)
        except (OverflowError, TypeError, ValueError) as exc:
            raise ValueError(error) from exc
        if array.ndim != 1 or array.size == 0:
            raise ValueError(error)
    if not np.isfinite(array).all():
        raise ValueError(f"{label} must be a non-empty finite one-dimensional sequence")
    return array


def _finite_model_output(values: Sequence[float], label: str) -> np.ndarray:
    # Model callbacks commonly return exact float64 arrays. Keep the same
    # shape/finiteness contract without routing this hot path through the
    # general sequence and ndarray-subclass normalization logic.
    if type(values) is np.ndarray and values.dtype == _FLOAT_DTYPE:
        if values.ndim != 1 or values.size == 0 or not np.isfinite(values).all():
            raise ValueError(f"{label} must be a non-empty finite one-dimensional sequence")
        return values
    return _finite_vector(values, label)


def _first_order_conversion_validated(times: np.ndarray, rate_constant: float) -> np.ndarray:
    return -np.expm1(-rate_constant * times)


def _first_order_objective_interval_lower_bound(
    times: np.ndarray,
    observed: np.ndarray,
    normalized_weights: np.ndarray,
    weight_sum: float,
    lower: float,
    upper: float,
) -> float:
    """Return a conservative floating-point lower bound for one rate interval.

    For non-negative times, the first-order conversion is monotone in rate, so
    each prediction on ``[lower, upper]`` lies between the endpoint predictions.
    The distance-to-interval bound is valid component by component. A Taylor
    lower bound may tighten it: ``J(m) - |J'(m)| h - M h**2 / 2``, where ``M``
    bounds ``|J''|`` on the interval. The explicit outward pads make the bound
    conservative for ordinary binary64/libm rounding; this is not formal
    interval arithmetic over real numbers.
    """

    epsilon = np.finfo(float).eps
    prediction_pad = 16.0 * epsilon
    objective_pad = 64.0 * epsilon * max(1.0, weight_sum)
    try:
        with np.errstate(over="ignore", under="ignore", invalid="ignore"):
            prediction_lower = _first_order_conversion_validated(times, lower)
            prediction_upper = _first_order_conversion_validated(times, upper)
            prediction_lower = np.maximum(0.0, prediction_lower - prediction_pad)
            prediction_upper = np.minimum(1.0, prediction_upper + prediction_pad)
            residual_lower = np.nextafter(prediction_lower - observed, -np.inf)
            residual_upper = np.nextafter(prediction_upper - observed, np.inf)
            distance = np.maximum(0.0, np.maximum(residual_lower, -residual_upper))
            distance_terms = normalized_weights * distance * distance
        if not np.isfinite(distance_terms).all():
            return 0.0
        distance_lower_bound = max(
            0.0,
            math.nextafter(
                math.fsum(float(value) for value in distance_terms) - objective_pad, -math.inf
            ),
        )

        midpoint = lower + (upper - lower) / 2.0
        half_width = (upper - lower) / 2.0
        if midpoint == lower or midpoint == upper:
            return distance_lower_bound

        with np.errstate(over="ignore", under="ignore", invalid="ignore"):
            midpoint_prediction = _first_order_conversion_validated(times, midpoint)
            midpoint_residual = midpoint_prediction - observed
            midpoint_decay = np.exp(-midpoint * times)
            midpoint_terms = normalized_weights * midpoint_residual * midpoint_residual
            scaled_time = times * half_width
            linear_terms = (
                2.0 * normalized_weights * midpoint_residual * scaled_time * midpoint_decay
            )
            linear_scale_terms = 2.0 * normalized_weights * scaled_time * midpoint_decay
            left_decay = np.exp(-lower * times)
            left_decay_upper = np.minimum(1.0, left_decay + prediction_pad)
            curvature_terms = (
                normalized_weights
                * scaled_time
                * scaled_time
                * left_decay_upper
                * (2.0 * left_decay_upper + np.abs(1.0 - observed))
            )
        if not all(
            np.isfinite(values).all()
            for values in (
                midpoint_terms,
                linear_terms,
                linear_scale_terms,
                curvature_terms,
            )
        ):
            return distance_lower_bound

        midpoint_objective = math.fsum(float(value) for value in midpoint_terms)
        linear_term = math.fsum(float(value) for value in linear_terms)
        linear_magnitude = math.fsum(abs(float(value)) for value in linear_terms)
        linear_scale = math.fsum(float(value) for value in linear_scale_terms)
        curvature = math.fsum(float(value) for value in curvature_terms)
        if not all(math.isfinite(value) for value in (midpoint_objective, linear_term, curvature)):
            return distance_lower_bound

        midpoint_error = (
            math.fsum(
                float(weight) * (2.0 * abs(float(residual)) * prediction_pad + prediction_pad**2)
                for weight, residual in zip(normalized_weights, midpoint_residual, strict=True)
            )
            + objective_pad
        )
        midpoint_lower_bound = max(0.0, midpoint_objective - midpoint_error)
        linear_error = 64.0 * epsilon * (linear_magnitude + linear_scale)
        linear_upper = math.nextafter(abs(linear_term) + linear_error, math.inf)
        curvature_upper = math.nextafter(curvature * (1.0 + 64.0 * epsilon), math.inf)
        with np.errstate(over="ignore", under="ignore", invalid="ignore"):
            taylor_lower_bound = (
                midpoint_lower_bound - linear_upper - curvature_upper - objective_pad
            )
        if not math.isfinite(taylor_lower_bound):
            return distance_lower_bound
        return max(distance_lower_bound, max(0.0, taylor_lower_bound))
    except (OverflowError, ValueError):
        # An unusable Taylor enclosure must only make the search less decisive.
        return 0.0


def first_order_conversion(times_s: Sequence[float], rate_constant_s: float) -> np.ndarray:
    times = _finite_vector(times_s, "times_s")
    if np.any(times < 0):
        raise ValueError("times_s must be non-negative")
    rate_constant = _finite_scalar(rate_constant_s, "rate_constant_s")
    if rate_constant < 0:
        raise ValueError("rate_constant_s must be finite and non-negative")
    return _first_order_conversion_validated(times, rate_constant)


def fit_first_order_rate(
    times_s: Sequence[float],
    conversion: Sequence[float],
    *,
    lower_s: float = 0.0,
    upper_s: float = 10.0,
    weights: Sequence[float] | None = None,
    iterations: int = 96,
    global_search_iterations: int = 96,
    global_objective_tolerance_fraction: float = 1e-12,
) -> dict[str, Any]:
    """Bounded one-parameter least-squares reference fit.

    Golden-section search supplies a local candidate. Since the objective is
    non-negative, a feasible seed already within the requested gap of zero is
    certified immediately; otherwise a bounded branch-and-bound pass compares
    it with interval lower bounds. The pass stops only when its floating-point
    objective-gap fraction is within tolerance or its split budget is exhausted.
    An unconverged result remains ``HOLD`` even when local information is positive.

    ``times_s`` uses seconds, ``rate_constant_s`` uses inverse seconds, and
    conversion is dimensionless. The objective-gap tolerance is a fraction of
    the total positive weight, not a parameter-error or scientific-approval
    tolerance. Floating-point pads are conservative working enclosures, not
    formal interval arithmetic or industrial parameter release.
    """
    times = _finite_vector(times_s, "times_s")
    observed = _finite_vector(conversion, "conversion")
    if observed.shape != times.shape:
        raise ValueError("times_s and conversion must have the same length")
    if np.any(times < 0):
        raise ValueError("times_s must be non-negative")
    if np.any((observed < 0) | (observed > 1)):
        raise ValueError("conversion values must lie in [0, 1]")
    lower = _finite_scalar(lower_s, "lower_s")
    upper = _finite_scalar(upper_s, "upper_s")
    if lower < 0:
        raise ValueError("rate bounds must be finite with lower_s >= 0")
    if lower >= upper:
        raise ValueError("lower_s must be less than upper_s")
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations < 16:
        raise ValueError("iterations must be an integer >= 16")
    if (
        isinstance(global_search_iterations, bool)
        or not isinstance(global_search_iterations, int)
        or global_search_iterations < 0
    ):
        raise ValueError("global_search_iterations must be an integer >= 0")
    tolerance_fraction = _finite_scalar(
        global_objective_tolerance_fraction, "global_objective_tolerance_fraction"
    )
    if not 0.0 < tolerance_fraction <= 1.0:
        raise ValueError("global_objective_tolerance_fraction must lie in (0, 1]")
    if weights is None:
        weight_array = np.ones_like(times)
    else:
        weight_array = _finite_vector(weights, "weights")
        if weight_array.shape != times.shape or np.any(weight_array <= 0):
            raise ValueError("weights must match observations and be positive")
    weight_scale = float(np.max(weight_array))
    with np.errstate(under="ignore"):
        normalized_weights = weight_array / weight_scale
    weight_sum = (
        float(times.size)
        if weights is None
        else math.fsum(float(value) for value in normalized_weights)
    )
    if not math.isfinite(weight_sum) or weight_sum <= 0:
        raise ValueError("weight normalization exceeds the finite range")

    def objective_values(rate: float) -> tuple[float, float]:
        residual = _first_order_conversion_validated(times, rate) - observed
        value = (
            float(np.dot(residual, residual))
            if weights is None
            else float(np.sum(weight_array * residual * residual))
        )
        if not math.isfinite(value):
            raise ValueError("weighted fit objective exceeds the finite range")
        normalized_value = (
            value if weights is None else float(np.sum(normalized_weights * residual * residual))
        )
        if not math.isfinite(normalized_value):
            raise ValueError("normalized fit objective exceeds the finite range")
        return value, normalized_value

    def objective(rate: float) -> float:
        return objective_values(rate)[0]

    ratio = (math.sqrt(5.0) - 1.0) / 2.0
    left, right = lower, upper
    x1 = right - ratio * (right - left)
    x2 = left + ratio * (right - left)
    f1, f2 = objective(x1), objective(x2)
    for _ in range(iterations):
        if f1 <= f2:
            right, x2, f2 = x2, x1, f1
            x1 = right - ratio * (right - left)
            f1 = objective(x1)
        else:
            left, x1, f1 = x1, x2, f2
            x2 = left + ratio * (right - left)
            f2 = objective(x2)
    fitted = left + (right - left) / 2.0

    best_rate = fitted
    best_objective, best_normalized_objective = objective_values(best_rate)
    boundary_tolerance = 8.0 * np.finfo(float).eps * max(1.0, abs(lower), abs(upper))
    if best_rate - lower <= boundary_tolerance:
        candidate_objective, candidate_normalized_objective = objective_values(lower)
        if candidate_normalized_objective <= best_normalized_objective:
            best_rate = lower
            best_objective = candidate_objective
            best_normalized_objective = candidate_normalized_objective
    if upper - best_rate <= boundary_tolerance:
        candidate_objective, candidate_normalized_objective = objective_values(upper)
        if candidate_normalized_objective <= best_normalized_objective:
            best_rate = upper
            best_objective = candidate_objective
            best_normalized_objective = candidate_normalized_objective
    roundoff_pad = 64.0 * np.finfo(float).eps * max(1.0, weight_sum)
    tolerance = tolerance_fraction * weight_sum
    search_iterations = 0
    if best_normalized_objective + roundoff_pad <= tolerance:
        # J(k) is non-negative everywhere. This feasible seed therefore
        # closes the requested global gap against the exact lower bound zero.
        # Keep the legacy exact-model hot path free of interval and heap work.
        global_lower_bound = 0.0
        global_gap = best_normalized_objective + roundoff_pad
        global_gap_fraction = global_gap / weight_sum
        optimization_converged = True
    else:
        for candidate in (lower, upper):
            candidate_objective, candidate_normalized_objective = objective_values(candidate)
            if candidate_normalized_objective < best_normalized_objective:
                best_rate = candidate
                best_objective = candidate_objective
                best_normalized_objective = candidate_normalized_objective

        interval_heap = [
            (
                _first_order_objective_interval_lower_bound(
                    times, observed, normalized_weights, weight_sum, lower, upper
                ),
                lower,
                upper,
            )
        ]
        pruned_lower_bound = math.inf

        def objective_gap() -> tuple[float, float, float]:
            candidate_upper = best_normalized_objective + roundoff_pad
            current_lower = min(
                interval_heap[0][0] if interval_heap else math.inf,
                pruned_lower_bound,
            )
            if not math.isfinite(current_lower) or current_lower > candidate_upper:
                # Numerical enclosure inconsistency must reduce confidence, never
                # manufacture a zero gap.
                current_lower = 0.0
            current_lower = max(0.0, current_lower)
            gap = max(0.0, candidate_upper - current_lower)
            return current_lower, gap, gap / weight_sum

        while interval_heap and search_iterations < global_search_iterations:
            _lower_bound, interval_lower, interval_upper = interval_heap[0]
            _current_lower, _gap, gap_fraction = objective_gap()
            if gap_fraction <= tolerance_fraction:
                break
            heapq.heappop(interval_heap)
            midpoint = interval_lower + (interval_upper - interval_lower) / 2.0
            if midpoint == interval_lower or midpoint == interval_upper:
                heapq.heappush(interval_heap, (_lower_bound, interval_lower, interval_upper))
                break

            midpoint_objective, midpoint_normalized_objective = objective_values(midpoint)
            if midpoint_normalized_objective < best_normalized_objective:
                best_rate = midpoint
                best_objective = midpoint_objective
                best_normalized_objective = midpoint_normalized_objective

            prune_threshold = best_normalized_objective + roundoff_pad - tolerance
            for child_lower, child_upper in (
                (interval_lower, midpoint),
                (midpoint, interval_upper),
            ):
                child_bound = _first_order_objective_interval_lower_bound(
                    times,
                    observed,
                    normalized_weights,
                    weight_sum,
                    child_lower,
                    child_upper,
                )
                if child_bound >= prune_threshold:
                    pruned_lower_bound = min(pruned_lower_bound, child_bound)
                else:
                    heapq.heappush(interval_heap, (child_bound, child_lower, child_upper))
            search_iterations += 1

        global_lower_bound, global_gap, global_gap_fraction = objective_gap()
        optimization_converged = bool(global_gap_fraction <= tolerance_fraction)
    fitted = best_rate
    predicted = _first_order_conversion_validated(times, fitted)
    residual = predicted - observed
    rmse = float(np.sqrt(np.mean(residual**2)))
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        sensitivity = times * np.exp(-fitted * times)
        information_value = float(np.sum(weight_array * sensitivity * sensitivity))
    information = information_value if math.isfinite(information_value) else None
    identifiable = information > 1e-12 if information is not None else None
    time_design_varies = float(np.ptp(times)) > 0
    return {
        "status": "CALCULATED_REFERENCE_ONLY"
        if identifiable is True and optimization_converged
        else "HOLD",
        "rate_constant_s": fitted,
        "objective": best_objective,
        "rmse": rmse,
        "information_scalar": information,
        "identifiable": identifiable,
        "time_design_varies": time_design_varies,
        "bounds_s": [lower, upper],
        "optimization_converged": optimization_converged,
        "global_objective_lower_bound_fraction": float(global_lower_bound / weight_sum),
        "global_objective_gap_fraction": float(global_gap_fraction),
        "global_objective_tolerance_fraction": tolerance_fraction,
        "global_search_iterations": search_iterations,
        "global_search_iteration_budget": global_search_iterations,
        "scientific_approval": "NOT_EVALUATED",
    }


def finite_difference_jacobian(
    model: Callable[[np.ndarray], Sequence[float]],
    parameters: Sequence[float],
    *,
    relative_step: float = 1e-6,
    parameter_scales: Sequence[float] | None = None,
) -> np.ndarray:
    """Compute a central-difference Jacobian using optional parameter scales.

    Omitting ``parameter_scales`` preserves the historical unit-scale step.
    Otherwise, each finite positive characteristic scale sets the floor for
    that parameter's relative step. Callers must keep both perturbations in the
    model's valid domain. The returned observation-by-parameter matrix owns
    column-contiguous storage; callbacks may reuse their output buffers.
    """
    params = _finite_vector(parameters, "parameters")
    relative_step_value = _finite_scalar(relative_step, "relative_step")
    if relative_step_value <= 0:
        raise ValueError("relative_step must be finite and positive")
    scales = (
        None if parameter_scales is None else _finite_vector(parameter_scales, "parameter_scales")
    )
    if scales is not None and (scales.shape != params.shape or np.any(scales <= 0)):
        raise ValueError("parameter_scales must match parameters and be positive")
    baseline = _finite_model_output(model(params.copy()), "model output")
    # A model may reuse and resize its output buffer during later callbacks.
    # Freeze the dimension contract before any such mutation can affect it.
    baseline_shape = baseline.shape
    # Each callback fills one column. Keep those snapshots contiguous, also
    # matching the column-oriented layout consumed by the downstream SVD.
    jacobian = np.empty((baseline_shape[0], params.size), dtype=float, order="F")
    limits = np.finfo(float)
    safe_perturbations = (
        scales is None
        and limits.eps <= relative_step_value <= 1.0
        and float(np.max(np.abs(params))) <= limits.max / 4.0
    )
    lower_values = np.empty_like(jacobian)
    denominators = np.empty(params.size, dtype=float)

    # Snapshot callback results because models may reuse mutable output buffers.
    # Retain lower outputs so derivative arithmetic can be vectorized after all
    # callbacks, outside their NumPy error-policy context.
    for index, value in enumerate(params):
        scalar = float(value)
        reference_scale = (
            max(1.0, abs(scalar)) if scales is None else max(abs(scalar), float(scales[index]))
        )
        step = relative_step_value * reference_scale
        denominator = 2.0 * step
        if safe_perturbations:
            upper_value = scalar + step
            lower_value = scalar - step
        else:
            if not math.isfinite(step) or not math.isfinite(denominator):
                raise ValueError("finite-difference step exceeds the finite range")
            upper_value = scalar + step
            lower_value = scalar - step
            if not math.isfinite(upper_value) or not math.isfinite(lower_value):
                raise ValueError("finite-difference perturbation exceeds the finite range")
            if upper_value == scalar or lower_value == scalar:
                raise ValueError("finite-difference step is too small to perturb the parameter")
        plus = params.copy()
        minus = params.copy()
        plus[index] = upper_value
        minus[index] = lower_value
        upper = _finite_model_output(model(plus), "model output")
        if upper.shape != baseline_shape:
            raise ValueError("model output shape changed during finite differences")
        jacobian[:, index] = upper
        lower = _finite_model_output(model(minus), "model output")
        if lower.shape != baseline_shape:
            raise ValueError("model output shape changed during finite differences")
        lower_values[:, index] = lower
        denominators[index] = denominator
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        np.subtract(jacobian, lower_values, out=jacobian)
        np.divide(jacobian, denominators, out=jacobian)
    if not np.isfinite(jacobian).all():
        raise ValueError("finite-difference derivative exceeds the finite range")
    return jacobian


def assess_identifiability(
    jacobian: Sequence[Sequence[float]], *, condition_limit: float = 1e8
) -> dict[str, Any]:
    error = "jacobian must be a non-empty finite matrix"
    if isinstance(jacobian, np.ndarray) and jacobian.dtype.kind in "iuf":
        if jacobian.ndim != 2 or jacobian.size == 0:
            raise ValueError(error)
        try:
            matrix = np.asarray(jacobian, dtype=float)
        except (OverflowError, TypeError, ValueError) as exc:
            raise ValueError(error) from exc
        if not np.isfinite(matrix).all():
            raise ValueError(error)
    else:
        try:
            rows = tuple(
                _finite_vector(row, f"jacobian[{index}]") for index, row in enumerate(jacobian)
            )
        except TypeError as exc:
            raise ValueError(error) from exc
        if not rows or any(row.shape != rows[0].shape for row in rows):
            raise ValueError(error)
        matrix = np.vstack(rows)
    limit = _finite_scalar(condition_limit, "condition_limit")
    if limit <= 1:
        raise ValueError("condition_limit must be finite and greater than one")

    # The ordinary path keeps the original unscaled SVD so representative
    # Jacobians do not pay for an additional max/abs/divide pass. Some finite
    # matrices near the IEEE-754 limits can nevertheless overflow or underflow
    # inside SVD. Only then retry after one positive global scale; rank and the
    # 2-norm condition number are invariant to that scale, unlike per-column
    # normalization which could hide genuine parameter ill-conditioning.
    try:
        with np.errstate(over="ignore", invalid="ignore", under="ignore"):
            singular = np.linalg.svd(matrix, compute_uv=False)
    except np.linalg.LinAlgError:
        singular = np.asarray([], dtype=float)

    needs_scaled_retry = singular.size != min(matrix.shape) or not np.isfinite(singular).all()
    if not needs_scaled_retry and singular.size and singular[-1] == 0.0 and np.any(matrix != 0.0):
        needs_scaled_retry = True

    if needs_scaled_retry:
        scale = float(np.max(np.abs(matrix)))
        if scale == 0.0:
            singular = np.zeros(min(matrix.shape), dtype=float)
        else:
            with np.errstate(over="ignore", invalid="ignore", under="ignore"):
                singular = np.linalg.svd(matrix / scale, compute_uv=False)

        # The first result was checked when deciding whether to retry. Validate
        # the replacement here without scanning an unchanged result twice.
        if not np.isfinite(singular).all():
            raise ValueError("jacobian singular values exceed the finite range")

    tolerance = max(matrix.shape) * np.finfo(float).eps * singular[0]
    rank = int(np.sum(singular > tolerance))
    full_rank = rank == matrix.shape[1]
    condition = None if not full_rank else float(singular[0] / singular[-1])
    if condition is not None and not math.isfinite(condition):
        condition = None
    status = "PASS" if condition is not None and condition <= limit else "HOLD"
    return {
        "status": status,
        "rank": rank,
        "parameters": matrix.shape[1],
        "observations": matrix.shape[0],
        "condition_number": condition,
        "condition_status": (
            "RANK_DEFICIENT" if not full_rank else "NONFINITE" if condition is None else "DEFINED"
        ),
        "condition_limit": limit,
        "scientific_approval": "NOT_EVALUATED",
    }
