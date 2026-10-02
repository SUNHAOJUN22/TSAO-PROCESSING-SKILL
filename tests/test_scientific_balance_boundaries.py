from __future__ import annotations

import json

import pytest

from tsao.science import balance_residual, closure_fraction


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
