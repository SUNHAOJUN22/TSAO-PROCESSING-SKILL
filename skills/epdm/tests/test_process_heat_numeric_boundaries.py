from __future__ import annotations

import math
from decimal import Decimal, localcontext

import pytest

from skills.epdm.process import (
    entropy_generation_heat_transfer_kW_K,
    grade_transition_offspec_fraction,
    heat_removal_margin,
)


def entropy_reference(duty: float, hot: float, cold: float) -> float:
    with localcontext() as context:
        context.prec = 80
        return float(
            Decimal.from_float(duty) * (1 / Decimal.from_float(cold) - 1 / Decimal.from_float(hot))
        )


@pytest.mark.parametrize("cold", [273.15, 298.15, 300.0, 323.15, 400.0, 1000.0])
def test_entropy_preserves_a_resolved_near_isothermal_temperature_gap(cold: float) -> None:
    hot = math.nextafter(cold, math.inf)
    actual = entropy_generation_heat_transfer_kW_K(80.0, hot, cold)
    expected = entropy_reference(80.0, hot, cold)
    assert actual > 0.0
    assert actual == pytest.approx(expected, rel=3e-15, abs=0.0)


def test_entropy_retains_a_finite_result_when_reciprocal_temperature_overflows() -> None:
    duty, hot, cold = 1e-320, 1e-308, 5e-309
    result = entropy_generation_heat_transfer_kW_K(duty, hot, cold)
    assert result == pytest.approx(entropy_reference(duty, hot, cold), rel=3e-15, abs=0.0)


def test_zero_heat_duty_has_zero_entropy_even_at_small_positive_temperatures() -> None:
    assert entropy_generation_heat_transfer_kW_K(0.0, 1e-308, 5e-309) == 0.0


@pytest.mark.parametrize("args", [(1e308, 2.0, 0.25), (1e-308, 1e308, 5e307)])
def test_unrepresentable_nonzero_entropy_is_a_domain_error(args: tuple[float, ...]) -> None:
    with pytest.raises(ValueError, match="finite|representable"):
        entropy_generation_heat_transfer_kW_K(*args)


def test_unrepresentable_heat_removal_margin_is_a_domain_error() -> None:
    with pytest.raises(ValueError, match="finite|representable"):
        heat_removal_margin(1e308, 1e-308)


@pytest.mark.parametrize("scale", [1e-308, 1.0, 1e308])
def test_heat_removal_margin_preserves_its_fractional_basis(scale: float) -> None:
    assert heat_removal_margin(0.8 * scale, scale) == pytest.approx(0.2)
    assert heat_removal_margin(scale, scale) == 0.0


@pytest.mark.parametrize(
    "residence,transition,expected",
    [(1e308, 1e308, 0.5), (1.5e308, 1e308, 0.4), (1e308, 1.5e308, 0.6)],
)
def test_transition_fraction_survives_an_overflowing_total_duration(
    residence: float, transition: float, expected: float
) -> None:
    assert grade_transition_offspec_fraction(residence, transition) == pytest.approx(expected)


def test_transition_fraction_preserves_zero_and_saturated_limits() -> None:
    assert grade_transition_offspec_fraction(1e308, 0.0) == 0.0
    assert grade_transition_offspec_fraction(1e-308, 1e308) == 1.0


def test_positive_transition_fraction_cannot_underflow_to_a_false_zero() -> None:
    with pytest.raises(ValueError, match="finite|representable"):
        grade_transition_offspec_fraction(1e308, 1e-308)
