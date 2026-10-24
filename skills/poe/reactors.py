from __future__ import annotations

import math
from typing import Any

from tsao.numeric_contract import finite, finite_product, finite_sum


def _nonnegative(value: float, label: str) -> float:
    result = finite(value, label)
    if result < 0:
        raise ValueError(f"{label} must be finite and non-negative")
    return result


def _bounded_exposure(rate: float, residence: float) -> float:
    """Multiply non-negative rate and residence, preserving bounded overflow semantics."""
    exposure = rate * residence
    if math.isinf(exposure):
        # Every bounded first-order conversion has rounded to one at this scale.
        return math.inf
    if exposure == 0.0 and rate > 0.0 and residence > 0.0:
        raise ValueError("rate-residence exposure underflows the nonzero floating-point range")
    return exposure


def first_order_pfr_conversion(rate_constant_s: float, residence_time_s: float) -> float:
    rate = _nonnegative(rate_constant_s, "rate_constant_s")
    residence = _nonnegative(residence_time_s, "residence_time_s")
    exposure = _bounded_exposure(rate, residence)
    return -math.expm1(-exposure)


def first_order_cstr_conversion(rate_constant_s: float, residence_time_s: float) -> float:
    rate = _nonnegative(rate_constant_s, "rate_constant_s")
    residence = _nonnegative(residence_time_s, "residence_time_s")
    damkohler = _bounded_exposure(rate, residence)
    if math.isinf(damkohler):
        return 1.0
    return damkohler / (1.0 + damkohler)


def first_order_cstr_series_conversion(
    rate_constant_s: float, total_residence_time_s: float, reactors: int
) -> float:
    rate = _nonnegative(rate_constant_s, "rate_constant_s")
    residence = _nonnegative(total_residence_time_s, "total_residence_time_s")
    if isinstance(reactors, bool) or not isinstance(reactors, int) or reactors <= 0:
        raise ValueError("reactors must be a positive integer")
    exposure = _bounded_exposure(rate, residence)
    if math.isinf(exposure):
        return 1.0
    per_reactor = exposure / reactors
    if per_reactor == 0.0 and exposure > 0.0:
        log_total_exposure = exposure
    else:
        try:
            log_total_exposure = reactors * math.log1p(per_reactor)
        except OverflowError:
            log_total_exposure = math.inf
    return -math.expm1(-log_total_exposure)


def heat_removal_margin(
    heat_generation_W: float,
    overall_U_W_m2_K: float,
    area_m2: float,
    driving_temperature_K: float,
    *,
    minimum_margin_fraction: float = 0.15,
) -> dict[str, Any]:
    generation = _nonnegative(heat_generation_W, "heat_generation_W")
    coefficient = _nonnegative(overall_U_W_m2_K, "overall_U_W_m2_K")
    area = _nonnegative(area_m2, "area_m2")
    driving = _nonnegative(driving_temperature_K, "driving_temperature_K")
    minimum_margin = _nonnegative(minimum_margin_fraction, "minimum_margin_fraction")
    capacity = _checked_capacity(coefficient, area, driving)
    if generation == 0:
        margin: float | None = None
        reason_code = "UNBOUNDED_MARGIN_ZERO_LOAD" if capacity > 0 else "ZERO_LOAD_ZERO_CAPACITY"
        status = "PASS" if capacity > 0 else "HOLD"
    else:
        difference = finite_sum((capacity, -generation), label="heat removal margin numerator")
        margin = finite_product(difference, divisor=generation, label="heat removal margin")
        reason_code = (
            "MARGIN_ACCEPTABLE"
            if capacity >= generation and margin >= minimum_margin
            else "MARGIN_INSUFFICIENT"
        )
        status = "PASS" if reason_code == "MARGIN_ACCEPTABLE" else "HOLD"
    return {
        "status": status,
        "reason_code": reason_code,
        "heat_generation_W": generation,
        "heat_removal_capacity_W": capacity,
        "margin_fraction": margin,
        "minimum_margin_fraction": minimum_margin,
        "engineering_approval": "NOT_EVALUATED",
    }


def _checked_capacity(coefficient: float, area: float, driving: float) -> float:
    return finite_product(coefficient, area, driving, label="heat-removal capacity")


def reactor_reference_suite(rate_constant_s: float, residence_time_s: float) -> dict[str, Any]:
    return {
        "status": "CALCULATED_REFERENCE_ONLY",
        "pfr_conversion": first_order_pfr_conversion(rate_constant_s, residence_time_s),
        "cstr_conversion": first_order_cstr_conversion(rate_constant_s, residence_time_s),
        "two_cstr_conversion": first_order_cstr_series_conversion(
            rate_constant_s, residence_time_s, 2
        ),
        "scientific_approval": "NOT_EVALUATED",
    }
