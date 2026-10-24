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
    if np.any(times < 0) or np.any(np.diff(times) < 0):
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
    effective = np.maximum(0.0, times - checked["dead_time_s"])
    response = checked["initial_output"] + checked["gain"] * checked["input_step"] * (
        1.0 - np.exp(-effective / checked["time_constant_s"])
    )
    response[times < checked["dead_time_s"]] = checked["initial_output"]
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
    if abs(change) < 1e-15:
        raise ValueError("target must differ from initial response")
    normalized = (values - initial) / change

    def first_cross(level: float) -> float | None:
        indices = np.flatnonzero(normalized >= level)
        return float(times[indices[0]]) if indices.size else None

    t10 = first_cross(0.1)
    t90 = first_cross(0.9)
    rise = None if t10 is None or t90 is None else t90 - t10
    band = 0.02 * abs(change)
    violations = np.flatnonzero(np.abs(values - target_value) > band)
    if not violations.size:
        settling = float(times[0])
    else:
        candidate = int(violations[-1]) + 1
        settling = float(times[candidate]) if candidate < values.size else None
    overshoot = max(0.0, float(np.max(normalized) - 1.0))
    iae = float(_trapezoid(np.abs(values - target_value), times))
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
