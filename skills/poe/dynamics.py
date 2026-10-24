from __future__ import annotations

import math
from collections.abc import Sequence
from numbers import Real
from typing import Any

import numpy as np

# NumPy 1.26 is part of the public dependency contract; ``trapezoid`` was
# introduced in 2.0 and the equivalent ``trapz`` was removed in 2.4. Resolve
# lazily so the unavailable name is never evaluated on either supported line.
_trapezoid = np.trapezoid if hasattr(np, "trapezoid") else np.trapz


def _finite_scalar(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{label} must be a finite real number; Boolean is rejected")
    try:
        number = float(value)
    except (OverflowError, TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be finite") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def _finite_vector(values: Sequence[float], label: str) -> np.ndarray:
    error = f"{label} must be a non-empty finite one-dimensional sequence"
    if isinstance(values, np.ndarray):
        if values.ndim != 1 or values.size == 0:
            raise ValueError(error)
        if values.dtype.kind == "b":
            _finite_scalar(values[0], f"{label}[0]")
        if values.dtype.kind not in "iuf":
            raise ValueError(error)
        array = np.asarray(values, dtype=float)
    else:
        try:
            raw_values = tuple(values)
        except TypeError as exc:
            raise ValueError(error) from exc
        if not raw_values:
            raise ValueError(error)
        for index, value in enumerate(raw_values):
            if isinstance(value, bool):
                _finite_scalar(value, f"{label}[{index}]")
            if not isinstance(value, Real):
                raise ValueError(error)
        try:
            array = np.asarray(raw_values, dtype=float)
        except (OverflowError, TypeError, ValueError) as exc:
            raise ValueError(error) from exc
    if array.ndim != 1 or array.size == 0 or not np.isfinite(array).all():
        raise ValueError(error)
    return array


def fopdt_response(
    times_s: Sequence[float],
    *,
    gain: float,
    time_constant_s: float,
    dead_time_s: float = 0.0,
    input_step: float = 1.0,
    initial_output: float = 0.0,
) -> np.ndarray:
    times = _finite_vector(times_s, "times_s")
    if times[0] < 0 or np.any(times[1:] < times[:-1]):
        raise ValueError("times_s must be non-negative and non-decreasing")
    parameters = {
        "gain": gain,
        "time_constant_s": time_constant_s,
        "dead_time_s": dead_time_s,
        "input_step": input_step,
        "initial_output": initial_output,
    }
    checked = {label: _finite_scalar(value, label) for label, value in parameters.items()}
    if checked["time_constant_s"] <= 0 or checked["dead_time_s"] < 0:
        raise ValueError("time_constant_s must be positive and dead_time_s non-negative")
    response_scale = checked["gain"] * checked["input_step"]
    if not math.isfinite(response_scale):
        raise ValueError("FOPDT response exceeds the finite range")
    # expm1 avoids cancellation when the dimensionless time is small.  Keep
    # overflow visible as a domain error instead of returning NaN/Inf as if it
    # were a usable model response.
    with np.errstate(over="ignore", invalid="ignore", under="ignore", divide="ignore"):
        # Sorted input makes the dead-time plateau a prefix. Fill it once, then
        # use the private result buffer for only the positive-time tail.
        response = np.empty_like(times)
        active_start = int(np.searchsorted(times, checked["dead_time_s"], side="right"))
        response[:active_start] = checked["initial_output"]
        dimensionless_time = response[active_start:]
        np.subtract(times[active_start:], checked["dead_time_s"], out=dimensionless_time)
        np.divide(dimensionless_time, checked["time_constant_s"], out=dimensionless_time)
        # The input validation above makes dimensionless_time non-decreasing.
        # Use expm1 for the cancellation-sensitive prefix and exp for the
        # well-conditioned remainder, then reuse the private array throughout.
        stable_count = int(np.searchsorted(dimensionless_time, 0.1, side="left"))
        stable_prefix = dimensionless_time[:stable_count].copy()
        np.negative(dimensionless_time, out=dimensionless_time)
        np.exp(dimensionless_time, out=dimensionless_time)
        np.subtract(1.0, dimensionless_time, out=dimensionless_time)
        if stable_count:
            np.negative(stable_prefix, out=stable_prefix)
            np.expm1(stable_prefix, out=stable_prefix)
            np.negative(stable_prefix, out=stable_prefix)
            dimensionless_time[:stable_count] = stable_prefix
        np.multiply(dimensionless_time, response_scale, out=dimensionless_time)
        np.add(dimensionless_time, checked["initial_output"], out=dimensionless_time)
    if not np.isfinite(response).all():
        raise ValueError("FOPDT response exceeds the finite range")
    return response


def response_metrics(
    times_s: Sequence[float], response: Sequence[float], *, target: float
) -> dict[str, Any]:
    times = _finite_vector(times_s, "times_s")
    values = _finite_vector(response, "response")
    if times.shape != values.shape or np.any(np.diff(times) < 0):
        raise ValueError("times_s and response must have equal, non-decreasing samples")
    target_value = _finite_scalar(target, "target")
    initial = float(values[0])
    change = target_value - initial
    if not math.isfinite(change):
        raise ValueError("target change exceeds the finite range")
    if change == 0.0:
        raise ValueError("target must differ from initial response")
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        normalized = (values - initial) / change
    if not np.isfinite(normalized).all():
        raise ValueError("normalized response exceeds the finite range")

    def first_cross(level: float) -> float | None:
        crossed = normalized >= level
        index = int(np.argmax(crossed))
        return float(times[index]) if crossed[index] else None

    t10 = first_cross(0.1)
    t90 = first_cross(0.9)
    rise = None if t10 is None or t90 is None else t90 - t10
    band = 0.02 * abs(change)
    absolute_error = np.abs(values - target_value)
    violations = absolute_error > band
    last_violation = violations.size - 1 - int(np.argmax(violations[::-1]))
    if not violations[last_violation]:
        settling = float(times[0])
    else:
        candidate = last_violation + 1
        settling = float(times[candidate]) if candidate < values.size else None
    overshoot = max(0.0, float(np.max(normalized) - 1.0))
    iae = float(_trapezoid(absolute_error, times))
    if any(
        value is not None and not math.isfinite(value) for value in (rise, settling, overshoot, iae)
    ):
        raise ValueError("response metrics exceed the finite range")
    return {
        "rise_time_s": rise,
        "settling_time_s": settling,
        "overshoot_fraction": overshoot,
        "integral_absolute_error": iae,
        "status": "CALCULATED_REFERENCE_ONLY",
        "engineering_approval": "NOT_EVALUATED",
    }


def recycle_memory_time(volume_m3: float, purge_flow_m3_s: float) -> dict[str, Any]:
    volume = _finite_scalar(volume_m3, "volume_m3")
    purge = _finite_scalar(purge_flow_m3_s, "purge_flow_m3_s")
    if not math.isfinite(volume) or volume <= 0:
        raise ValueError("volume_m3 must be finite and positive")
    if not math.isfinite(purge) or purge < 0:
        raise ValueError("purge_flow_m3_s must be finite and non-negative")
    if purge == 0:
        return {
            "status": "HOLD",
            "time_constant_s": None,
            "blocker": "zero purge gives unbounded ideal recycle memory",
            "engineering_approval": "NOT_EVALUATED",
        }
    return {
        "status": "CALCULATED_REFERENCE_ONLY",
        "time_constant_s": volume / purge,
        "engineering_approval": "NOT_EVALUATED",
    }


def grade_transition_assessment(
    times_s: Sequence[float], response: Sequence[float], *, target: float, max_settling_s: float
) -> dict[str, Any]:
    maximum_settling = _finite_scalar(max_settling_s, "max_settling_s")
    if maximum_settling <= 0:
        raise ValueError("max_settling_s must be finite and positive")
    metrics = response_metrics(times_s, response, target=target)
    settling = metrics["settling_time_s"]
    status = "PASS" if settling is not None and settling <= maximum_settling else "HOLD"
    return {**metrics, "status": status, "max_settling_s": maximum_settling}
