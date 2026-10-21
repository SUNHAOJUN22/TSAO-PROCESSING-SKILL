"""Finite arithmetic for physical quantities; overflow is not a valid balance."""

from __future__ import annotations

import math
from collections.abc import Iterable
from decimal import Decimal, localcontext
from fractions import Fraction


def finite(value: object, label: str = "quantity") -> float:
    # Physical arithmetic reuses checked binary floats.  Preserve the full
    # coercion contract for external values without repeating it on this path.
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"{label} must be finite")
        return value
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError(f"{label} must be a finite real number")
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError(f"{label} is outside the finite numeric range") from exc
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    if isinstance(value, str) and number == 0 and Decimal(value.strip()) != 0:
        raise ValueError(f"{label} underflows the nonzero floating-point range")
    return number


def finite_sum(values: Iterable[float], *, label: str = "sum") -> float:
    items = [finite(value, label) for value in values]
    try:
        result = math.fsum(items)
    except OverflowError:
        # Exact binary-rational summation preserves a subnormal residual even
        # after intermediate sums exceed float range. Fixed decimal precision
        # cannot guarantee that for cancellation across hundreds of exponents.
        try:
            result = float(sum((Fraction(value) for value in items), Fraction(0)))
        except OverflowError as exc:
            raise ValueError(f"{label} exceeds the finite floating-point range") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} exceeds the finite floating-point range")
    return result


def finite_product(*values: float, divisor: float = 1.0, label: str = "product") -> float:
    denominator = finite(divisor, label)
    if denominator == 0:
        raise ValueError(f"{label} has a zero divisor")
    # A single IEEE-754 operation is already correctly rounded.  These common
    # paths need no Decimal context, but still reject overflow and loss of a
    # nonzero result to underflow.  Validate both factors even when one is zero.
    if len(values) == 1:
        numerator = finite(values[0], label)
        result = numerator / denominator
        if not math.isfinite(result) or result == 0 and numerator != 0:
            raise ValueError(f"{label} is outside the representable nonzero finite range")
        return result
    if len(values) == 2 and denominator == 1.0:
        left = finite(values[0], label)
        right = finite(values[1], label)
        result = left * right
        if not math.isfinite(result) or result == 0 and left != 0 and right != 0:
            raise ValueError(f"{label} is outside the representable nonzero finite range")
        return result
    with localcontext() as context:
        context.prec = 80
        product = Decimal(1)
        for value in values:
            product *= Decimal.from_float(finite(value, label))
        product /= Decimal.from_float(denominator)
        result = float(product)
    if not math.isfinite(result) or result == 0 and product != 0:
        raise ValueError(f"{label} is outside the representable nonzero finite range")
    return result
