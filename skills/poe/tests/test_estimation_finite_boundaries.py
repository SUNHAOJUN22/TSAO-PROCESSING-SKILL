from __future__ import annotations

import json

import numpy as np
import pytest

from skills.poe.estimation import finite_difference_jacobian, fit_first_order_rate


@pytest.mark.parametrize("value,step", [(1.0, 1e-300), (1e308, 2.0), (1.7e308, 0.1)])
def test_unrepresentable_perturbations_rejected_before_model_call(value, step):
    calls = []

    def model(parameters):
        calls.append(parameters.copy())
        return [1.0]

    with pytest.raises(ValueError, match="finite-difference"):
        finite_difference_jacobian(model, [value], relative_step=step)
    assert len(calls) == 1


def test_nonfinite_derivative_is_not_returned():
    def model(parameters):
        return [1e308 if parameters[0] > 0 else -1e308]

    with pytest.raises(ValueError, match="derivative"):
        finite_difference_jacobian(model, [0.0])


def test_weighted_objective_overflow_is_not_a_fit_result():
    with np.errstate(over="ignore", invalid="ignore"):
        with pytest.raises(ValueError, match="objective"):
            fit_first_order_rate([1, 2, 3], [0, 0, 0], weights=[1e308] * 3)


def test_large_finite_bounds_have_finite_midpoint():
    with np.errstate(over="ignore", invalid="ignore"):
        result = fit_first_order_rate([1, 2], [0.5, 0.8], lower_s=1.6e308, upper_s=1.7e308)
    assert 1.6e308 <= result["rate_constant_s"] <= 1.7e308
    json.dumps(result, allow_nan=False)


def test_normal_analytic_jacobian_is_preserved():
    actual = finite_difference_jacobian(lambda x: [x[0] ** 2, 3 * x[0]], [2.0])
    np.testing.assert_allclose(actual, [[4.0], [3.0]], rtol=1e-8)
