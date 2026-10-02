from __future__ import annotations

import math
from collections.abc import Iterable
from fractions import Fraction

import numpy as np

from ._utils import validate_flow_mapping


def _finite_sum(values: Iterable[float], *, label: str) -> float:
    terms = tuple(values)
    try:
        result = math.fsum(terms)
    except OverflowError:
        # Preserve the submitted binary values under otherwise overflowing cancellation.
        exact = sum((Fraction.from_float(value) for value in terms), Fraction())
        try:
            result = float(exact)
        except OverflowError as exc:
            raise ValueError(f"{label} exceeds the finite floating-point range") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must remain finite")
    return result


def balance_residual(
    inputs: dict[str, float],
    outputs: dict[str, float],
    generation: dict[str, float] | None = None,
) -> dict[str, float]:
    checked_inputs = validate_flow_mapping("inputs", inputs, allow_negative=False)
    checked_outputs = validate_flow_mapping("outputs", outputs, allow_negative=False)
    checked_generation = validate_flow_mapping(
        "generation", {} if generation is None else generation, allow_negative=True
    )
    keys = set(checked_inputs) | set(checked_outputs) | set(checked_generation)
    return {
        key: _finite_sum(
            (
                checked_inputs.get(key, 0.0),
                checked_generation.get(key, 0.0),
                -checked_outputs.get(key, 0.0),
            ),
            label=f"balance residual {key!r}",
        )
        for key in sorted(keys)
    }


def closure_fraction(inputs: dict[str, float], outputs: dict[str, float]) -> float:
    checked_inputs = validate_flow_mapping("inputs", inputs, allow_negative=False)
    checked_outputs = validate_flow_mapping("outputs", outputs, allow_negative=False)
    total_in = _finite_sum(checked_inputs.values(), label="total input")
    if total_in <= 0:
        raise ValueError("input total must be positive")
    total_out = _finite_sum(checked_outputs.values(), label="total output")
    result = 1.0 - abs(total_in - total_out) / total_in
    if not math.isfinite(result):
        raise ValueError("closure fraction exceeds the finite floating-point range")
    return result


def stoichiometric_rank(matrix: list[list[float]]) -> int:
    try:
        values = np.asarray(matrix, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("rectangular numeric matrix required") from exc
    if values.ndim != 2 or values.size == 0 or 0 in values.shape:
        raise ValueError("non-empty 2D matrix required")
    if not np.isfinite(values).all():
        raise ValueError("matrix values must be finite")
    # A common nonzero scalar preserves rank while avoiding overflowing
    # singular values (a finite 3x3 matrix of 1e308 has a singular value 3e308).
    scale = float(np.max(np.abs(values)))
    if scale == 0.0:
        return 0
    return int(np.linalg.matrix_rank(values / scale))
