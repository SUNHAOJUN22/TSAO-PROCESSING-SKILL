from __future__ import annotations

import math
from fractions import Fraction

import pytest

from skills.poe.kinetics import KineticState, _state_add_vector

FIELDS = tuple(KineticState.__dataclass_fields__)


@pytest.mark.parametrize("index", range(len(FIELDS)))
def test_each_stage_component_rejects_nonfinite_values(index: int) -> None:
    # A NaN after a positive first component must not hide in a min/max check.
    state = [1.0] * len(FIELDS)
    state[index] = 0.0
    for invalid in (math.nan, math.inf, -math.inf):
        derivative = [0.0] * len(FIELDS)
        derivative[index] = invalid
        with pytest.raises(ValueError) as caught:
            _state_add_vector(tuple(state), tuple(derivative), 1.0)
        assert str(caught.value) == f"integration produced non-finite {FIELDS[index]}: {invalid}"


@pytest.mark.parametrize("index", range(len(FIELDS)))
def test_each_stage_component_keeps_tolerance_and_positive_zero(index: int) -> None:
    for value in (0.0, -0.0, -1e-10, math.nextafter(-1e-10, 0.0)):
        state = [1.0] * len(FIELDS)
        derivative = [0.0] * len(FIELDS)
        state[index] = value
        # Preserve a negative zero through multiplication/addition before clipping.
        derivative[index] = -0.0
        result = _state_add_vector(tuple(state), tuple(derivative), 1.0)
        assert result[index].hex() == "0x0.0p+0"
        assert result[:index] + result[index + 1 :] == (1.0,) * (len(FIELDS) - 1)

    state[index] = math.nextafter(-1e-10, -math.inf)
    with pytest.raises(ValueError) as caught:
        _state_add_vector(tuple(state), tuple(derivative), 1.0)
    assert str(caught.value) == (
        f"integration produced materially negative {FIELDS[index]}: {state[index]}"
    )


@pytest.mark.parametrize(
    "state,derivative,factor",
    [
        (1.0, 2.0**-53, 1.0),
        (1.0, 3.0 * 2.0**-53, 1.0),
        (1.0, -(1.0 - 2.0**-52), 1.0 + 2.0**-52),
        (0.0, math.ulp(0.0), 0.5),
        (0.0, 3.0 * math.ulp(0.0), 0.5),
        (1e308, -1e308, 1.0),
        (1.0, 1.0, -0.25),
        (1e-300, 1e-300, 2.0**-52),
    ],
)
def test_stage_multiply_then_add_rounding_is_bit_exact(
    state: float, derivative: float, factor: float
) -> None:
    # Independent rational arithmetic rounds once after multiplication and again
    # after addition. This detects reassociation, fused operations and underflow
    # changes; approximate numerical equality would miss these cases.
    rounded_product = float(Fraction(factor) * Fraction(derivative))
    expected = float(Fraction(state) + Fraction(rounded_product))
    if expected <= 0.0:
        expected = 0.0
    result = _state_add_vector(
        (state,) * len(FIELDS), (derivative,) * len(FIELDS), factor
    )
    assert [value.hex() for value in result] == [expected.hex()] * len(FIELDS)


@pytest.mark.parametrize("invalid", [math.nan, math.inf, -math.inf, -1.0])
def test_stage_errors_keep_first_component_order(invalid: float) -> None:
    state = (0.0,) * len(FIELDS)
    derivative = [0.0] * len(FIELDS)
    derivative[3] = invalid
    derivative[8] = math.nan
    expected_kind = "non-finite" if not math.isfinite(invalid) else "materially negative"
    with pytest.raises(ValueError) as caught:
        _state_add_vector(state, tuple(derivative), 1.0)
    assert str(caught.value) == f"integration produced {expected_kind} {FIELDS[3]}: {invalid}"


@pytest.mark.parametrize("index", [0, len(FIELDS) - 1])
def test_stage_overflow_is_rejected_before_clipping(index: int) -> None:
    state = [1.0] * len(FIELDS)
    derivative = [0.0] * len(FIELDS)
    state[index] = 1e308
    derivative[index] = 1e308
    with pytest.raises(ValueError) as caught:
        _state_add_vector(tuple(state), tuple(derivative), 2.0)
    assert str(caught.value) == f"integration produced non-finite {FIELDS[index]}: inf"
