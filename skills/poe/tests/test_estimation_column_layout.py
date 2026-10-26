from __future__ import annotations

import numpy as np
import pytest

from skills.poe.estimation import assess_identifiability, finite_difference_jacobian


@pytest.mark.parametrize("shape", [(3, 5), (200, 8)])
@pytest.mark.parametrize("strided", [False, True])
def test_rectangular_jacobian_copies_reused_callback_columns(
    shape: tuple[int, int], strided: bool
) -> None:
    observations, parameters = shape
    design = np.random.default_rng(42).normal(size=shape)
    point = np.linspace(0.5, 2.0, parameters)
    storage = np.empty(observations * (2 if strided else 1))
    output = storage[::2] if strided else storage

    def model(values: np.ndarray) -> np.ndarray:
        output[:] = design @ (values * values)
        return output

    actual = finite_difference_jacobian(model, point)
    # Direct analytic derivative, independent of differencing or array layout.
    expected = 2.0 * design * point
    np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=2e-9)
    output.fill(0.0)
    np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=2e-9)


def test_nonfinite_svd_retry_remains_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def nonfinite_svd(matrix: np.ndarray, *, compute_uv: bool) -> np.ndarray:
        assert compute_uv is False
        calls.append(matrix.copy())
        return np.array([np.inf, 1.0])

    monkeypatch.setattr(np.linalg, "svd", nonfinite_svd)
    with pytest.raises(ValueError, match="singular values exceed the finite range"):
        assess_identifiability([[4.0, 0.0], [0.0, 2.0]])
    assert len(calls) == 2
    np.testing.assert_array_equal(calls[1], [[1.0, 0.0], [0.0, 0.5]])
