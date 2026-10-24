from __future__ import annotations

import numpy as np
import pytest

from skills.poe.estimation import finite_difference_jacobian


@pytest.mark.parametrize("view", [False, True])
def test_jacobian_snapshots_a_reused_model_output(view: bool) -> None:
    buffer = np.zeros(4)

    def model(parameters: np.ndarray) -> np.ndarray:
        x, y = parameters
        buffer[:] = [x * x, 3 * x, y * y, 2 * y]
        return buffer[::2] if view else buffer

    actual = finite_difference_jacobian(model, [2.0, 3.0])
    expected = np.array([[4.0, 0.0], [3.0, 0.0], [0.0, 6.0], [0.0, 2.0]])
    np.testing.assert_allclose(actual, expected[::2] if view else expected, rtol=1e-8, atol=1e-10)


@pytest.mark.parametrize("resize_on_call", [2, 3])
def test_jacobian_rejects_resizing_the_baseline_output_buffer(resize_on_call: int) -> None:
    buffer = np.empty(2)
    calls = 0

    def model(parameters: np.ndarray) -> np.ndarray:
        nonlocal calls
        calls += 1
        if calls >= resize_on_call:
            buffer.resize((1,), refcheck=False)
        buffer[0] = parameters[0] ** 2
        if buffer.size == 2:
            buffer[1] = 3.0 * parameters[0]
        return buffer

    with pytest.raises(ValueError, match="model output shape changed"):
        finite_difference_jacobian(model, [2.0])
    assert calls == resize_on_call  # Reject the first changed shape without more callbacks.
