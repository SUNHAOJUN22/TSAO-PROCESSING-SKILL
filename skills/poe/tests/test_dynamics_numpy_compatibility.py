from __future__ import annotations

from decimal import Decimal, localcontext

import numpy as np
import pytest

from skills.poe.core import fopdt_response, grade_transition_assessment, response_metrics


def test_response_metrics_preserves_exact_piecewise_linear_area() -> None:
    # Unit-width trapezoids have areas 0.75, 0.255 and 0.005.
    result = response_metrics([0, 1, 2, 3], [0, 0.5, 0.99, 1.0], target=1.0)
    assert result["integral_absolute_error"] == pytest.approx(1.01)
    assert result["settling_time_s"] == 2.0
    assert result["engineering_approval"] == "NOT_EVALUATED"


def test_grade_transition_public_entrypoint_keeps_approval_boundary() -> None:
    result = grade_transition_assessment(
        [0, 1, 2, 3], [0, 0.5, 0.99, 1.0], target=1.0, max_settling_s=3.0
    )
    assert result["status"] == "PASS"
    assert result["integral_absolute_error"] == pytest.approx(1.01)
    assert result["engineering_approval"] == "NOT_EVALUATED"


def test_irregular_time_grid_uses_actual_intervals() -> None:
    # Absolute error is a triangle of height 4 and width 4: exact area 8.
    result = response_metrics([0, 1, 4], [0, 1, 4], target=4.0)
    assert result["integral_absolute_error"] == pytest.approx(8.0)


def test_fopdt_small_dimensionless_time_matches_first_order_reference() -> None:
    # For z=t/tau << 1, 1-exp(-z) = z + O(z^2); the stable result should
    # retain the representable first-order response instead of cancelling to 0.
    actual = fopdt_response([0.0, 1e-20], gain=1.0, time_constant_s=1.0)
    assert actual[1] == pytest.approx(1e-20, rel=1e-15, abs=0.0)


def _decimal_fopdt_reference(
    time_s: float,
    *,
    gain: float,
    time_constant_s: float,
    dead_time_s: float = 0.0,
    input_step: float = 1.0,
    initial_output: float = 0.0,
) -> float:
    # Evaluate the analytical solution at 80 decimal digits from the exact
    # binary64 inputs. This oracle does not reuse NumPy's exp/expm1 or the
    # production floating-point subtraction and scaling operations.
    with localcontext() as context:
        context.prec = 80
        elapsed = max(Decimal(0), Decimal.from_float(time_s) - Decimal.from_float(dead_time_s))
        exponent = -elapsed / Decimal.from_float(time_constant_s)
        return float(
            Decimal.from_float(initial_output)
            + Decimal.from_float(gain)
            * Decimal.from_float(input_step)
            * (Decimal(1) - exponent.exp())
        )


@pytest.mark.parametrize("dimensionless_time", [1e-20, 1e-16, 1e-12, 1e-8, 0.1, 1.0, 10.0])
@pytest.mark.parametrize("gain", [1.0, -1.0, 1e16, 1e-200])
def test_fopdt_matches_independent_decimal_solution(dimensionless_time: float, gain: float) -> None:
    expected = _decimal_fopdt_reference(dimensionless_time, gain=gain, time_constant_s=1.0)
    actual = fopdt_response([0.0, dimensionless_time], gain=gain, time_constant_s=1.0)
    assert actual[0] == 0.0
    # A relative bound is required: an absolute 1e-12 allowance would accept
    # zero for most of the small responses this regression is meant to protect.
    assert actual[1] == pytest.approx(expected, rel=2e-15, abs=0.0)


@pytest.mark.parametrize("time_scale", [2.0**-100, 1.0, 2.0**100])
def test_fopdt_dead_time_and_signed_step_preserve_the_analytical_solution(
    time_scale: float,
) -> None:
    times = [value * time_scale for value in (0.0, 1.0, 2.0, 2.0 + 2.0**-40, 4.0, 50.0)]
    parameters = {
        "gain": -2.0,
        "time_constant_s": 5.0 * time_scale,
        "dead_time_s": 2.0 * time_scale,
        "input_step": 3.0,
        "initial_output": 0.0,
    }
    actual = fopdt_response(times, **parameters)
    expected = [_decimal_fopdt_reference(time, **parameters) for time in times]
    assert actual[:3].tolist() == [0.0, 0.0, 0.0]
    assert actual == pytest.approx(expected, rel=2e-15, abs=0.0)


def test_fopdt_saturation_and_offset_remain_finite_at_extreme_time_ratio() -> None:
    with np.errstate(all="raise"):
        actual = fopdt_response(
            [0.0, 1e308],
            gain=-2.0,
            time_constant_s=1e-308,
            input_step=-3.0,
            initial_output=7.0,
        )
    assert actual.tolist() == [7.0, 13.0]


def test_fopdt_rejects_unrepresentable_derived_response() -> None:
    with pytest.raises(ValueError, match="finite range"):
        fopdt_response([0.0, 1.0], gain=1e308, input_step=10.0, time_constant_s=1.0)


def test_response_metrics_are_invariant_to_representable_output_scale() -> None:
    scale = 2.0**-54
    times = [0.0, 1.0, 2.0, 3.0]
    values = [0.0, 0.5, 0.99, 1.0]
    baseline = response_metrics(times, values, target=1.0)
    scaled = response_metrics(times, [value * scale for value in values], target=scale)
    assert scaled["settling_time_s"] == baseline["settling_time_s"]
    assert scaled["rise_time_s"] == baseline["rise_time_s"]
    assert scaled["overshoot_fraction"] == pytest.approx(baseline["overshoot_fraction"])
    assert scaled["integral_absolute_error"] == pytest.approx(
        baseline["integral_absolute_error"] * scale, rel=1e-15, abs=0.0
    )
