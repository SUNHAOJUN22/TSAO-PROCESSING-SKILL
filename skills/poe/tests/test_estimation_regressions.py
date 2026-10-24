from __future__ import annotations

import json

import numpy as np
import pytest

from skills.poe.estimation import (
    assess_identifiability,
    finite_difference_jacobian,
    first_order_conversion,
    fit_first_order_rate,
)


def test_fixed_positive_time_can_identify_the_single_rate() -> None:
    times = [10.0, 10.0, 10.0]
    result = fit_first_order_rate(times, first_order_conversion(times, 0.1))
    assert result["identifiable"] is True
    assert result["rate_constant_s"] == pytest.approx(0.1, abs=1e-8)
    assert result["time_design_varies"] is False
    assert result["scientific_approval"] == "NOT_EVALUATED"


def test_zero_time_has_no_information() -> None:
    result = fit_first_order_rate([0.0, 0.0], [0.0, 0.0])
    assert result["identifiable"] is False
    assert result["status"] == "HOLD"


def test_small_conversion_does_not_cancel_to_zero() -> None:
    assert first_order_conversion([1e-20], 1.0)[0] == pytest.approx(1e-20, rel=1e-14, abs=0)


def test_boolean_values_are_not_accepted_as_scientific_numbers() -> None:
    with pytest.raises(ValueError, match="Boolean is rejected"):
        first_order_conversion([True], 1.0)
    with pytest.raises(ValueError, match="Boolean is rejected"):
        first_order_conversion([1.0], True)
    with pytest.raises(ValueError, match="Boolean is rejected"):
        fit_first_order_rate([1.0, 2.0], [0.2, 0.4], lower_s=True)
    with pytest.raises(ValueError, match="Boolean is rejected"):
        finite_difference_jacobian(lambda x: [x[0]], [True])
    with pytest.raises(ValueError, match="Boolean is rejected"):
        assess_identifiability([[True]])
    with pytest.raises(ValueError, match="Boolean is rejected"):
        assess_identifiability(np.array([[True, False]]))


@pytest.mark.parametrize("shape", [(2, 2), (0,)])
def test_array_subclasses_cannot_mask_invalid_storage_shape(shape: tuple[int, ...]) -> None:
    class MisleadingArray(np.ndarray):
        @property
        def ndim(self) -> int:
            return 1

        @property
        def size(self) -> int:
            return 1

    values = np.zeros(shape).view(MisleadingArray)
    with pytest.raises(ValueError, match="non-empty finite one-dimensional"):
        first_order_conversion(values, 0.5)


@pytest.mark.parametrize("matrix", [[[0.0, 0.0]], [[1.0, 2.0], [2.0, 4.0]]])
def test_rank_deficiency_is_strict_json(matrix: list[list[float]]) -> None:
    result = assess_identifiability(matrix)
    assert result["status"] == "HOLD"
    assert result["condition_number"] is None
    assert result["condition_status"] == "RANK_DEFICIENT"
    json.dumps(result, allow_nan=False)
