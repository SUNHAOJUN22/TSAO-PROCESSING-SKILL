from __future__ import annotations

import pytest

from skills.poe.core import grade_transition_assessment, response_metrics


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
