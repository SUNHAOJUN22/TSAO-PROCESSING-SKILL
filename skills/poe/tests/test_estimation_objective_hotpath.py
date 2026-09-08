from __future__ import annotations

import math

import numpy as np
import pytest

from skills.poe.estimation import first_order_conversion, fit_first_order_rate


@pytest.mark.parametrize("rate", [1e-6, 0.2, 2.0])
def test_unit_weight_hotpath_preserves_analytic_fit_and_explicit_weights(rate: float) -> None:
    times = np.linspace(0.0, 10.0, 101)
    observed = first_order_conversion(times, rate)
    implicit = fit_first_order_rate(times, observed, upper_s=3.0)
    explicit = fit_first_order_rate(times, observed, weights=np.ones_like(times), upper_s=3.0)
    assert implicit["rate_constant_s"] == pytest.approx(rate, rel=1e-10, abs=1e-12)
    assert implicit["rate_constant_s"] == pytest.approx(
        explicit["rate_constant_s"], rel=1e-10, abs=1e-12
    )
    residual = first_order_conversion(times, implicit["rate_constant_s"]) - observed
    expected = math.fsum(float(value) ** 2 for value in residual)
    assert implicit["objective"] == pytest.approx(expected, rel=1e-12, abs=1e-30)
    assert implicit["rmse"] < 1e-12
    assert implicit["scientific_approval"] == "NOT_EVALUATED"


def test_nonuniform_weighted_objective_keeps_its_weighted_definition() -> None:
    times = np.linspace(0.0, 10.0, 101)
    observed = first_order_conversion(times, 0.2) + 0.001 * np.sin(times)
    weights = np.linspace(0.25, 2.0, len(times))
    result = fit_first_order_rate(times, observed, weights=weights, upper_s=1.0)
    residual = first_order_conversion(times, result["rate_constant_s"]) - observed
    expected = math.fsum(float(w * r * r) for w, r in zip(weights, residual, strict=True))
    assert result["objective"] == pytest.approx(expected, rel=1e-12, abs=1e-30)
    assert result["scientific_approval"] == "NOT_EVALUATED"
