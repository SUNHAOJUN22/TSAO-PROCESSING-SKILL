from __future__ import annotations

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
    assert actual[1] == pytest.approx(1e-20, rel=1e-15)


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
        baseline["integral_absolute_error"] * scale
    )
