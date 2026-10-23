"""Dimensionless error must survive finite cancellation and mean scaling."""

import pytest

from tsao.contracts_v17 import mean_absolute_percentage_error


def test_mape_keeps_finite_ratio_despite_unrepresentable_intermediate_difference():
    assert mean_absolute_percentage_error([1e308], [-1e308]) == 2.0


def test_mape_keeps_finite_mean_despite_unrepresentable_term_sum():
    assert mean_absolute_percentage_error([1.0, 1.0], [1e308, 1e308]) == 1e308


def test_mape_rejects_unrepresentable_ratio_instead_of_returning_infinity():
    with pytest.raises(ValueError, match="finite"):
        mean_absolute_percentage_error([1e-308], [1e308])


def test_mape_cannot_drop_nonzero_observations_that_underflow_during_coercion():
    with pytest.raises(ValueError, match="underflow"):
        mean_absolute_percentage_error(["1e-999"], [0.0])


def test_mape_uses_only_nonzero_observations_and_preserves_all_zero_none():
    assert mean_absolute_percentage_error([0.0, 100.0], [999.0, 110.0]) == 0.1
    assert mean_absolute_percentage_error([0.0], [999.0]) is None


def test_mape_keeps_boolean_rejection():
    with pytest.raises(TypeError, match="boolean"):
        mean_absolute_percentage_error([True], [1.0])
