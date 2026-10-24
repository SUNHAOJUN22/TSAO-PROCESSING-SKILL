from __future__ import annotations

import math
from collections.abc import Sequence
from fractions import Fraction
from typing import Any

import numpy as np

from tsao.contracts_v17 import mean_absolute_percentage_error
from tsao.numeric_contract import finite, finite_product, finite_sum


def _finite_vector(values: Sequence[float], label: str) -> list[float]:
    array = np.asarray(values, dtype=object)
    if array.ndim != 1 or array.size == 0:
        raise ValueError(f"{label} must be a non-empty finite one-dimensional sequence")
    result = []
    for index, raw in enumerate(array):
        value = raw.item() if isinstance(raw, np.generic) else raw
        result.append(finite(value, f"{label}[{index}]"))
    return result


def regression_error_metrics(
    observed: Sequence[float], predicted: Sequence[float]
) -> dict[str, float | None]:
    actual = _finite_vector(observed, "observed")
    estimate = _finite_vector(predicted, "predicted")
    if len(actual) != len(estimate):
        raise ValueError("observed and predicted must have the same length")
    residual = [
        finite_sum((prediction, -measurement), label="regression residual")
        for measurement, prediction in zip(actual, estimate, strict=True)
    ]

    residual_scale = max(map(abs, residual), default=0.0)
    if residual_scale == 0.0:
        mae = rmse = 0.0
    else:
        normalized_errors = [abs(error) / residual_scale for error in residual]
        mae = residual_scale * (math.fsum(normalized_errors) / len(residual))
        rmse = residual_scale * math.sqrt(
            math.fsum(error * error for error in normalized_errors) / len(residual)
        )

    # A nonzero observed value is an eligible denominator at every scale. The
    # shared contract also represents an all-zero denominator set as None.
    mape = mean_absolute_percentage_error(actual, estimate)

    actual_scale = max(map(abs, actual), default=0.0)
    if actual_scale == 0.0:
        r2 = 1.0 if residual_scale == 0.0 else 0.0
    else:
        normalized_actual = [value / actual_scale for value in actual]
        normalized_mean = math.fsum(normalized_actual) / len(normalized_actual)
        centered = [value - normalized_mean for value in normalized_actual]
        centered_sum = math.fsum(value * value for value in centered)
        if centered_sum == 0.0:
            r2 = 1.0 if residual_scale == 0.0 else 0.0
        elif residual_scale == 0.0:
            r2 = 1.0
        else:
            normalized_residual = [error / residual_scale for error in residual]
            residual_sum = math.fsum(value * value for value in normalized_residual)
            scale_ratio = Fraction.from_float(residual_scale) / Fraction.from_float(actual_scale)
            ratio = (
                scale_ratio
                * scale_ratio
                * Fraction.from_float(residual_sum)
                / Fraction.from_float(centered_sum)
            )
            try:
                r2 = float(Fraction(1) - ratio)
            except OverflowError as exc:
                raise ValueError("R-squared exceeds the finite numeric range") from exc
            if not math.isfinite(r2):
                raise ValueError("R-squared exceeds the finite numeric range")
    return {"mae": mae, "rmse": rmse, "mape_fraction": mape, "r2": r2}


def power_law_viscosity(shear_rate_s: float, consistency_Pa_s_n: float, flow_index: float) -> float:
    shear = finite(shear_rate_s, "shear_rate_s")
    consistency = finite(consistency_Pa_s_n, "consistency_Pa_s_n")
    index = finite(flow_index, "flow_index")
    if shear <= 0 or consistency <= 0 or index <= 0:
        raise ValueError("rheology inputs must be positive")
    if index == 1.0:
        return consistency
    try:
        factor = math.pow(shear, index - 1.0)
    except OverflowError:
        factor = math.inf
    if math.isfinite(factor) and factor != 0.0:
        return finite_product(consistency, factor, label="power-law viscosity")

    # If the power alone lies outside float range, the product can still be
    # representable when consistency compensates. Evaluate the combined value
    # in log space and reject only an unrepresentable final viscosity.
    log_viscosity = math.log(consistency) + (index - 1.0) * math.log(shear)
    if not math.isfinite(log_viscosity):
        raise ValueError("power-law viscosity exceeds the finite representable range")
    try:
        viscosity = math.exp(log_viscosity)
    except OverflowError as exc:
        raise ValueError("power-law viscosity exceeds the finite representable range") from exc
    if not math.isfinite(viscosity) or viscosity == 0.0:
        raise ValueError("power-law viscosity is outside the finite representable range")
    return viscosity


def heat_transfer_margin(
    duty_W: float,
    area_m2: float,
    overall_U_W_m2_K: float,
    delta_temperature_K: float,
    *,
    minimum_margin_fraction: float = 0.15,
) -> dict[str, Any]:
    values = [
        finite(duty_W, "duty_W"),
        finite(area_m2, "area_m2"),
        finite(overall_U_W_m2_K, "overall_U_W_m2_K"),
        finite(delta_temperature_K, "delta_temperature_K"),
    ]
    if not all(value >= 0 for value in values):
        raise ValueError("heat-transfer inputs must be finite and non-negative")
    minimum_margin_fraction = finite(minimum_margin_fraction, "minimum_margin_fraction")
    if minimum_margin_fraction < 0:
        raise ValueError("minimum_margin_fraction must be finite and non-negative")
    duty, area, coefficient, delta_t = values
    capacity = finite_product(area, coefficient, delta_t, label="heat-transfer capacity")
    if duty == 0:
        margin: float | None = None
        reason_code = "UNBOUNDED_MARGIN_ZERO_LOAD" if capacity > 0 else "ZERO_LOAD_ZERO_CAPACITY"
        status = "PASS" if capacity > 0 else "HOLD"
    else:
        margin = finite_product(
            finite_sum((capacity, -duty), label="heat-transfer margin numerator"),
            divisor=duty,
            label="heat-transfer margin",
        )
        reason_code = (
            "MARGIN_ACCEPTABLE"
            if capacity >= duty and margin >= minimum_margin_fraction
            else "MARGIN_INSUFFICIENT"
        )
        status = "PASS" if reason_code == "MARGIN_ACCEPTABLE" else "HOLD"
    return {
        "status": status,
        "reason_code": reason_code,
        "capacity_W": capacity,
        "duty_W": duty,
        "margin_fraction": margin,
        "engineering_approval": "NOT_EVALUATED",
    }
