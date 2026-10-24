from __future__ import annotations

import decimal
import json
import math

import pytest

from skills.poe.core import (
    first_order_cstr_conversion,
    first_order_cstr_series_conversion,
    first_order_pfr_conversion,
    heat_removal_margin,
    heat_transfer_margin,
    power_law_viscosity,
    reactor_reference_suite,
    regression_error_metrics,
)


def _decimal_first_order_pfr(rate: float, residence: float) -> float:
    context = decimal.Context(prec=80)
    exposure = context.multiply(
        context.create_decimal_from_float(rate), context.create_decimal_from_float(residence)
    )
    return float(context.subtract(decimal.Decimal(1), context.exp(context.minus(exposure))))


def test_small_exposure_reactor_kernels_match_independent_decimal_reference() -> None:
    rate, residence = 1e-12, 1.0
    expected = _decimal_first_order_pfr(rate, residence)
    assert first_order_pfr_conversion(rate, residence) == pytest.approx(expected, rel=1e-15)
    assert first_order_pfr_conversion(rate, residence) != 0.0

    exposure = decimal.Decimal("1e-8")
    context = decimal.Context(prec=80)
    per_reactor = context.divide(exposure, decimal.Decimal(3))
    remaining = context.power(context.add(decimal.Decimal(1), per_reactor), decimal.Decimal(-3))
    expected_series = float(context.subtract(decimal.Decimal(1), remaining))
    actual_series = first_order_cstr_series_conversion(1e-8, 1.0, 3)
    assert actual_series == pytest.approx(expected_series, rel=1e-14)


def test_large_finite_reactor_exposure_remains_a_finite_bounded_conversion() -> None:
    assert first_order_cstr_conversion(1e308, 2.0) == 1.0
    assert reactor_reference_suite(1e308, 2.0)["cstr_conversion"] == 1.0
    json.dumps(reactor_reference_suite(1e308, 2.0), allow_nan=False)


@pytest.mark.parametrize(
    "function,args",
    [
        (heat_removal_margin, (1.0, 1e308, 1e308, 2.0)),
        (heat_transfer_margin, (1.0, 1e308, 1e308, 2.0)),
    ],
)
def test_overflowed_heat_capacity_is_rejected_instead_of_passed(function, args) -> None:
    with pytest.raises(ValueError, match="representable|finite"):
        function(*args)


def test_heat_capacity_product_can_recover_from_intermediate_overflow() -> None:
    result = heat_transfer_margin(1e307, 1e308, 1e308, 1e-308)
    assert result["status"] == "PASS"
    assert result["capacity_W"] == pytest.approx(1e308)
    assert result["margin_fraction"] == pytest.approx(9.0)
    json.dumps(result, allow_nan=False)


def test_regression_metrics_keep_tiny_nonzero_denominators_and_undefined_zero_mape() -> None:
    tiny = regression_error_metrics([1e-20], [0.0])
    assert tiny["mape_fraction"] == 1.0
    zero = regression_error_metrics([0.0, 0.0], [1.0, 2.0])
    assert zero["mape_fraction"] is None
    json.dumps(zero, allow_nan=False)


def test_regression_metrics_scale_before_squaring_large_values() -> None:
    result = regression_error_metrics([1e308, 9e307], [9e307, 1e308])
    assert math.isfinite(result["mae"])
    assert math.isfinite(result["rmse"])
    assert result["mae"] == pytest.approx(1e307)
    assert result["rmse"] == pytest.approx(1e307)
    assert math.isfinite(result["r2"])
    json.dumps(result, allow_nan=False)


def test_power_law_viscosity_raises_domain_error_for_unrepresentable_result() -> None:
    with pytest.raises(ValueError, match="representable"):
        power_law_viscosity(1e308, 1e308, 3.0)
