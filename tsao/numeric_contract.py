"""Finite arithmetic for physical quantities; overflow is not a valid balance."""

from __future__ import annotations

import math
from collections.abc import Iterable
from decimal import Decimal, localcontext
from fractions import Fraction


def finite(value: object, label: str = "quantity") -> float:
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
