from __future__ import annotations

import math
from decimal import Decimal
from fractions import Fraction

import numpy as np
import pytest

from skills.epdm import kinetics, process

VALIDATORS = (kinetics._finite, process._finite)


@pytest.mark.parametrize("validate", VALIDATORS)
@pytest.mark.parametrize("value", [0.0, -0.0, math.ulp(0.0), -math.ulp(0.0), 1.0, -1.0, 1e308])
def test_builtin_floats_keep_every_bit(validate, value: float) -> None:
    result = validate(value, "test quantity")
    assert type(result) is float
    assert result.hex() == value.hex()


@pytest.mark.parametrize("validate", VALIDATORS)
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, "nan", "inf", "-inf"])
def test_all_nonfinite_conversion_paths_are_rejected(validate, value: object) -> None:
    with pytest.raises(ValueError, match="^test quantity must be finite$"):
        validate(value, "test quantity")


@pytest.mark.parametrize("validate", VALIDATORS)
@pytest.mark.parametrize("value", [True, False, None, "not a number"])
def test_boolean_and_nonnumeric_inputs_keep_their_error(validate, value: object) -> None:
    with pytest.raises(ValueError, match="^test quantity must be numeric$"):
        validate(value, "test quantity")


@pytest.mark.parametrize("validate", VALIDATORS)
@pytest.mark.parametrize(
    "value,expected",
    [
        (2, 2.0),
        ("-0.0", -0.0),
        (Decimal("1.25"), 1.25),
        (Fraction(3, 2), 1.5),
        (np.float64(2.5), 2.5),
    ],
)
def test_other_numeric_inputs_keep_their_float_conversion(
    validate, value: object, expected: float
) -> None:
    result = validate(value, "test quantity")
    assert type(result) is float
    assert result.hex() == expected.hex()


@pytest.mark.parametrize("validate", VALIDATORS)
def test_float_subclass_conversion_is_called_exactly_once(validate) -> None:
    calls = []

    class ConvertedFloat(float):
        def __float__(self) -> float:
            calls.append("converted")
            return -0.0

    # An isinstance(float) shortcut would incorrectly return the underlying NaN
    # and bypass this accepted, explicitly overridden conversion protocol.
    result = validate(ConvertedFloat(math.nan), "test quantity")
    assert result.hex() == "-0x0.0p+0"
    assert calls == ["converted"]


@pytest.mark.parametrize("validate", VALIDATORS)
def test_conversion_failures_preserve_exception_chaining(validate) -> None:
    class InvalidConversion:
        def __float__(self) -> float:
            raise TypeError("conversion failed")

    with pytest.raises(ValueError, match="^test quantity must be numeric$") as caught:
        validate(InvalidConversion(), "test quantity")
    assert isinstance(caught.value.__cause__, TypeError)
    assert str(caught.value.__cause__) == "conversion failed"
    with pytest.raises(OverflowError):
        validate(10**1000, "test quantity")
