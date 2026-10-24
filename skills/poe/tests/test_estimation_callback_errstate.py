from __future__ import annotations

import numpy as np
import pytest

from skills.poe.estimation import finite_difference_jacobian


@pytest.mark.parametrize("operation", ["divide", "over", "invalid"])
def test_perturbed_models_preserve_callers_floating_point_errors(operation: str) -> None:
    calls = []

    def model(parameters: np.ndarray) -> np.ndarray:
        calls.append(parameters.copy())
        if parameters[0] == 1.0:
            return np.array([1.0])
        if operation == "divide":
            value = np.array([1.0]) / 0.0
        elif operation == "over":
            value = np.array([1e308]) * 1e308
        else:
            value = np.sqrt(np.array([-1.0]))
        # A finite return must not hide an exception requested by the caller.
        return np.nan_to_num(value, nan=0.0, posinf=0.0, neginf=0.0) + parameters[0] ** 2

    with np.errstate(all="raise"), pytest.raises(FloatingPointError):
        finite_difference_jacobian(model, [1.0])
    assert len(calls) == 2  # Baseline then the first perturbed call; fail fast.


def test_all_model_evaluations_observe_the_same_callers_error_policy() -> None:
    policies = []

    def model(parameters: np.ndarray) -> np.ndarray:
        policies.append(np.geterr())
        return parameters**2

    expected = {"divide": "warn", "over": "raise", "invalid": "ignore", "under": "ignore"}
    with np.errstate(**expected):
        result = finite_difference_jacobian(model, [1.0])
        assert np.geterr() == expected
    assert policies == [expected, expected, expected]
    np.testing.assert_allclose(result, [[2.0]], rtol=1e-9, atol=0)


def test_each_multicolumn_callback_observes_the_callers_error_policy() -> None:
    policies = []

    def model(parameters: np.ndarray) -> np.ndarray:
        policies.append(np.geterr().copy())
        return parameters**2

    expected = {"divide": "warn", "over": "raise", "invalid": "ignore", "under": "ignore"}
    with np.errstate(**expected):
        result = finite_difference_jacobian(model, [1.0, 2.0, 3.0])
        assert np.geterr() == expected
    assert policies == [expected] * 7
    np.testing.assert_allclose(result, np.diag([2.0, 4.0, 6.0]), rtol=1e-9, atol=0)


@pytest.mark.parametrize(
    ("output", "message"),
    [
        (np.array([True]), "Boolean is rejected"),
        (np.array([np.nan]), "non-empty finite one-dimensional sequence"),
    ],
)
def test_model_output_fast_path_preserves_strict_numeric_validation(
    output: np.ndarray, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        finite_difference_jacobian(lambda _: output, [1.0])
