from __future__ import annotations

import math

import numpy as np
import pytest

from skills.poe.dynamics import grade_transition_assessment, response_metrics


def _scalar_reference(times: list[float], values: list[float], target: float) -> dict:
    samples = [float(value) for value in values]
    change = target - samples[0]
    normalized = [(value - samples[0]) / change for value in samples]
    crossings = [
        next(
            (float(time) for time, value in zip(times, normalized, strict=True) if value >= level),
            None,
        )
        for level in (0.1, 0.9)
    ]
    # Scientific settling definition: every sample in the remaining suffix
    # must be inside the band. This does not share the optimized index search.
    settling = next(
        (
            float(times[index])
            for index in range(len(samples))
            if all(abs(value - target) <= 0.02 * abs(change) for value in samples[index:])
        ),
        None,
    )
    area = math.fsum(
        (right_t - left_t) * (abs(left_y - target) + abs(right_y - target)) / 2.0
        for left_t, right_t, left_y, right_y in zip(
            times[:-1], times[1:], samples[:-1], samples[1:], strict=True
        )
    )
    return {
        "rise_time_s": (
            None if crossings[0] is None or crossings[1] is None else crossings[1] - crossings[0]
        ),
        "settling_time_s": settling,
        "overshoot_fraction": max(0.0, max(normalized) - 1.0),
        "integral_absolute_error": area,
    }


@pytest.mark.parametrize(
    ("times", "values", "target"),
    [
        ([0, 1, 2, 3, 4], [0, 10, 90, 98, 100], 100.0),
        ([5, 6, 7, 8, 9], [100, 90, 10, 2, 0], 0.0),
        ([0, 1, 2], [0, 1, 5], 100.0),
        ([0, 1, 2], [0, 20, 50], 100.0),
        ([0, 1, 2, 3], [0, 50, 100, 80], 100.0),
        ([0, 1, 2, 3, 4, 5], [0, 110, 96, 100, 97, 100], 100.0),
        ([0, 1, 1, 2, 3, 4], [0, 10, 10, 90, 90, 100], 100.0),
        ([0], [0], 100.0),
        ([0, 1], [-1e307, 1e307], 1e307),
    ],
    ids=[
        "rise-boundaries",
        "fall",
        "no-crossing",
        "only-ten-percent",
        "last-outside",
        "oscillation",
        "plateau",
        "single",
        "large-representable",
    ],
)
def test_response_events_match_independent_scalar_reference(
    times: list[float], values: list[float], target: float
) -> None:
    expected = _scalar_reference(times, values, target)
    actual = response_metrics(times, values, target=target)
    for field in ("rise_time_s", "settling_time_s", "overshoot_fraction"):
        assert actual[field] == expected[field]
    assert actual["integral_absolute_error"] == pytest.approx(
        expected["integral_absolute_error"], rel=2e-15, abs=2e-15
    )
    assert actual["status"] == "CALCULATED_REFERENCE_ONLY"
    assert actual["engineering_approval"] == "NOT_EVALUATED"


@pytest.mark.parametrize(
    ("times", "values", "target", "maximum_settling"),
    [
        ([0.0, 1.0], [-1e308, 1e308], 1e308, 2.0),
        ([0.0, 1e308], [0.0, 10.0], 10.0, 1e308),
    ],
    ids=["unrepresentable-change", "unrepresentable-integral"],
)
def test_unrepresentable_metrics_cannot_pass_grade_assessment(
    times: list[float], values: list[float], target: float, maximum_settling: float
) -> None:
    # The API must reject invalid derived metrics even if a caller suppresses
    # NumPy floating-point warnings; a finite settling time alone is insufficient.
    with np.errstate(over="ignore", invalid="ignore"):
        with pytest.raises(ValueError, match="finite range"):
            response_metrics(times, values, target=target)
        with pytest.raises(ValueError, match="finite range"):
            grade_transition_assessment(
                times, values, target=target, max_settling_s=maximum_settling
            )
