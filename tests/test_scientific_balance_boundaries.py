from __future__ import annotations

import json

import numpy as np
import pytest

from tsao.science import balance_residual, closure_fraction, stoichiometric_rank


def test_finite_residual_survives_intermediate_overflow() -> None:
    result = balance_residual({"A": 1e308}, {"A": 1e308}, {"A": 1e308})
    assert result == {"A": 1e308}
    json.dumps(result, allow_nan=False)


def test_true_residual_overflow_is_a_domain_error() -> None:
    with pytest.raises(ValueError, match="finite"):
        balance_residual({"A": 1e308}, {}, {"A": 1e308})


def test_cancellation_preserves_small_remainders() -> None:
    assert balance_residual({"A": 1e308}, {"A": 1e308}, {"A": 1e-308}) == {"A": 1e-308}


@pytest.mark.parametrize("value", [True, False, 10**400])
def test_bool_and_unrepresentable_flows_are_rejected(value: object) -> None:
    with pytest.raises(ValueError):
        balance_residual({"A": value}, {})  # type: ignore[dict-item]


@pytest.mark.parametrize("generation", [False, [], ""])
def test_invalid_empty_generation_is_not_silently_replaced(generation: object) -> None:
    with pytest.raises(TypeError, match="mapping"):
        balance_residual({"A": 1.0}, {}, generation)  # type: ignore[arg-type]


def test_closure_ratio_rejects_overflow_without_clamping_real_imbalance() -> None:
    with pytest.raises(ValueError, match="finite"):
        closure_fraction({"A": 1e-308}, {"A": 1e308})
    with pytest.raises(ValueError, match="finite"):
        closure_fraction({"A": 1e308, "B": 1e308}, {})
    assert closure_fraction({"A": 1.0}, {"A": 3.0}) == -1.0
    assert closure_fraction({"A": 10.0}, {"A": 9.8}) == pytest.approx(0.98)


@pytest.mark.parametrize("scale", [1.0, 1e308, 1e-308, np.nextafter(0.0, 1.0)])
def test_rank_is_invariant_under_representable_common_scaling(scale: float) -> None:
    rank_one = [[scale] * 3 for _ in range(3)]
    diagonal = np.diag([scale] * 3).tolist()
    assert stoichiometric_rank(rank_one) == 1
    assert stoichiometric_rank(diagonal) == 3


def test_zero_stoichiometric_matrix_has_rank_zero() -> None:
    assert stoichiometric_rank([[0.0, 0.0], [0.0, 0.0]]) == 0


def test_rank_preserves_rectangular_dependencies() -> None:
    matrix = [[1.0, 2.0, -1.0], [2.0, 4.0, -2.0]]
    assert stoichiometric_rank(matrix) == 1
    assert stoichiometric_rank((np.asarray(matrix).T * 1e307).tolist()) == 1
