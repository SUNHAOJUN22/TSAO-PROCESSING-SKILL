from __future__ import annotations

import math
from decimal import Decimal, localcontext

from .numeric_contract import finite, finite_product, finite_sum

FARADAY_C_MOL = 96485.33212


def _finite(value: float, label: str) -> float:
    return finite(value, label)


def _decimal_result(value: Decimal, label: str) -> float:
    result = finite(float(value), label)
    if result == 0.0 and value != 0:
        raise ValueError(f"{label} underflows the nonzero floating-point range")
    return result


def cstr_first_order_conversion(k_s: float, residence_s: float) -> float:
    k_s = _finite(k_s, "rate constant")
    residence_s = _finite(residence_s, "residence time")
    if k_s < 0 or residence_s < 0:
        raise ValueError("rate constant and residence time must be non-negative")
    # The bounded conversion can be representable even when k*tau is not.
    with localcontext() as context:
        context.prec = 80
        da = Decimal.from_float(k_s) * Decimal.from_float(residence_s)
        return _decimal_result(da / (1 + da), "CSTR conversion")


def pfr_first_order_conversion(k_s: float, residence_s: float) -> float:
    k_s = _finite(k_s, "rate constant")
    residence_s = _finite(residence_s, "residence time")
    if k_s < 0 or residence_s < 0:
        raise ValueError("rate constant and residence time must be non-negative")
    exposure = k_s * residence_s
    if math.isinf(exposure):
        # Positive exposure beyond float range rounds exp(-exposure) to zero;
        # the final bounded conversion is exactly representable as 1.0.
        return 1.0
    exposure = finite_product(k_s, residence_s, label="PFR exposure")
    return -math.expm1(-exposure)


def oxygen_transfer_rate(kla_s: float, saturation: float, bulk: float) -> float:
    kla_s = _finite(kla_s, "kLa")
    saturation = _finite(saturation, "saturation concentration")
    bulk = _finite(bulk, "bulk concentration")
    if kla_s < 0 or saturation < 0 or bulk < 0:
        raise ValueError("kLa and concentrations must be non-negative")
    if bulk > saturation:
        raise ValueError("bulk concentration exceeds saturation; use a stripping model")
    return finite_product(
        kla_s,
        finite_sum((saturation, -bulk), label="oxygen concentration difference"),
        label="oxygen transfer rate",
    )


def faradaic_efficiency(
    product_mol: float, electron_number: float, current_A: float, time_s: float
) -> float:
    product_mol = _finite(product_mol, "product amount")
    electron_number = _finite(electron_number, "electron number")
    current_A = _finite(current_A, "current")
    time_s = _finite(time_s, "time")
    if (
        min(product_mol, current_A, time_s) < 0
        or electron_number <= 0
        or current_A == 0
        or time_s == 0
    ):
        raise ValueError("amount/current/time must be positive and electron number positive")
    # Evaluate the ratio before conversion to float: both charge products may
    # overflow independently while their dimensionless ratio remains finite.
    with localcontext() as context:
        context.prec = 80
        charge = (
            Decimal.from_float(product_mol)
            * Decimal.from_float(electron_number)
            * Decimal.from_float(FARADAY_C_MOL)
        )
        supplied = Decimal.from_float(current_A) * Decimal.from_float(time_s)
        efficiency = _decimal_result(charge / supplied, "Faradaic efficiency")
    if efficiency > 1.0 + 1e-9:
        raise ValueError("calculated Faradaic efficiency exceeds unity")
    return efficiency


def supersaturation_ratio(concentration: float, saturation_concentration: float) -> float:
    concentration = _finite(concentration, "concentration")
    saturation_concentration = _finite(saturation_concentration, "saturation concentration")
    if concentration < 0 or saturation_concentration <= 0:
        raise ValueError("concentration must be non-negative and saturation concentration positive")
    return finite_product(
        concentration, divisor=saturation_concentration, label="supersaturation ratio"
    )


def recycle_impurity_steady_state(
    fresh_input: float, recycle_fraction: float, purge_fraction: float
) -> float:
    fresh_input = _finite(fresh_input, "fresh impurity input")
    recycle_fraction = _finite(recycle_fraction, "recycle fraction")
    purge_fraction = _finite(purge_fraction, "purge fraction")
    if fresh_input < 0 or not 0 <= recycle_fraction < 1 or not 0 <= purge_fraction <= 1:
        raise ValueError("invalid fresh input, recycle fraction or purge fraction")
    retained = finite_product(recycle_fraction, 1.0 - purge_fraction, label="retained fraction")
    if retained >= 1.0:
        raise ValueError("recycle impurity network has no finite steady state")
    return finite_product(fresh_input, divisor=1.0 - retained, label="recycle impurity")


def semibatch_accumulation(feed_rate: float, consumption_rate: float, duration_s: float) -> float:
    feed_rate = _finite(feed_rate, "feed rate")
    consumption_rate = _finite(consumption_rate, "consumption rate")
    duration_s = _finite(duration_s, "duration")
    if feed_rate < 0 or consumption_rate < 0 or duration_s < 0:
        raise ValueError("rates and duration must be non-negative")
    return finite_product(
        finite_sum((feed_rate, -consumption_rate), label="net semibatch rate"),
        duration_s,
        label="semibatch accumulation",
    )


def availability(mtbf_h: float, mttr_h: float) -> float:
    mtbf_h = _finite(mtbf_h, "MTBF")
    mttr_h = _finite(mttr_h, "MTTR")
    if mtbf_h <= 0 or mttr_h < 0:
        raise ValueError("MTBF must be positive and MTTR non-negative")
    # Divide by the larger time before adding, so an overflowing sum cannot
    # turn equal finite MTBF/MTTR values into zero availability.
    if mtbf_h >= mttr_h:
        return 1.0 / (1.0 + mttr_h / mtbf_h)
    ratio = finite_product(mtbf_h, divisor=mttr_h, label="availability ratio")
    return finite_product(ratio, divisor=1.0 + ratio, label="availability")


def weibull_reliability(time: float, characteristic_life: float, shape: float) -> float:
    time = _finite(time, "time")
    characteristic_life = _finite(characteristic_life, "characteristic life")
    shape = _finite(shape, "shape")
    if time < 0 or characteristic_life <= 0 or shape <= 0:
        raise ValueError("time must be non-negative; life and shape positive")
    if time == 0.0:
        return 1.0
    # Work in logarithms so a large/small lifetime ratio can still yield a
    # representable hazard when the shape compensates. Near unity, log1p
    # preserves the difference between adjacent floating-point lifetimes.
    ratio = time / characteristic_life
    log_ratio = (
        math.log1p((time - characteristic_life) / characteristic_life)
        if 0.5 <= ratio <= 2.0
        else math.log(time) - math.log(characteristic_life)
    )
    log_hazard = shape * log_ratio
    if log_hazard > math.log(746.0):
        raise ValueError("Weibull reliability underflows the nonzero range")
    hazard = math.exp(log_hazard)
    reliability = math.exp(-hazard)
    if reliability == 0.0:
        raise ValueError("Weibull reliability underflows the nonzero range")
    return reliability


def process_capability_index(mean: float, sigma: float, lower: float, upper: float) -> float:
    mean = _finite(mean, "mean")
    sigma = _finite(sigma, "sigma")
    lower = _finite(lower, "lower specification")
    upper = _finite(upper, "upper specification")
    if sigma <= 0 or lower >= upper:
        raise ValueError("sigma must be positive and lower specification below upper")
    with localcontext() as context:
        context.prec = 80
        center = Decimal.from_float(mean)
        width = 3 * Decimal.from_float(sigma)
        index = min(
            (Decimal.from_float(upper) - center) / width,
            (center - Decimal.from_float(lower)) / width,
        )
        return _decimal_result(index, "process capability index")
