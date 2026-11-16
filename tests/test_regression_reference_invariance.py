"""A shared physical reference origin cannot improve a regression's R-squared."""

from __future__ import annotations

from fractions import Fraction

import pytest

from skills.poe.properties import regression_error_metrics


def reference_r2(observed, predicted):
    actual = list(map(Fraction, observed))
    estimates = list(map(Fraction, predicted))
    mean = sum(actual) / len(actual)
    residual = sum(
        (estimate - value) ** 2 for value, estimate in zip(actual, estimates, strict=True)
    )
    variation = sum((value - mean) ** 2 for value in actual)
    return float(1 - residual / variation)


@pytest.mark.parametrize("origin", [0.0, 1e6, 1e12, 1e16, -1e16])
@pytest.mark.parametrize("predictions", [[2.0, 2.0, 2.0], [0.0, 2.0, 2.0]])
def test_reference_translation_preserves_r_squared(origin, predictions):
    observed = [origin + value for value in (0.0, 2.0, 4.0)]
    predicted = [origin + value for value in predictions]
    metrics = regression_error_metrics(observed, predicted)
    assert metrics["r2"] == pytest.approx(reference_r2(observed, predicted), abs=1e-14)
    unshifted = regression_error_metrics([0.0, 2.0, 4.0], predictions)
    assert metrics["mae"] == unshifted["mae"]
    assert metrics["rmse"] == unshifted["rmse"]


def test_wide_signed_target_range_retains_the_finite_metric():
    observed = [-1e308, 1e308]
    predicted = [-5e307, 5e307]
    assert regression_error_metrics(observed, predicted)["r2"] == pytest.approx(
        reference_r2(observed, predicted)
    )
