from __future__ import annotations

import json
import math

import numpy as np
import pytest

from skills.poe.estimation import (
    _first_order_objective_interval_lower_bound,
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


def test_exact_fit_closes_gap_against_nonnegative_objective_without_interval_search(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected_interval_bound(*args: object) -> float:
        pytest.fail("a zero-feasible objective gap needs no interval search")

    monkeypatch.setattr(
        "skills.poe.estimation._first_order_objective_interval_lower_bound",
        unexpected_interval_bound,
    )
    times = np.linspace(0.0, 20.0, 401)
    result = fit_first_order_rate(times, first_order_conversion(times, 0.2), upper_s=1.0)

    assert result["rate_constant_s"] == pytest.approx(0.2, abs=1e-12)
    assert result["optimization_converged"] is True
    assert result["global_objective_lower_bound_fraction"] == 0.0
    assert result["global_objective_gap_fraction"] <= result["global_objective_tolerance_fraction"]
    assert result["global_search_iterations"] == 0


def test_multipeak_fit_beats_independent_feasible_point_and_reports_gap() -> None:
    times = [0.11625890971846743, 12.249747272130165, 21.830648874490496]
    observed = [0.3524257328950935, 0.3685787023335362, 0.8036058964092736]
    result = fit_first_order_rate(
        times,
        observed,
        lower_s=0.0,
        upper_s=2.0,
        weights=[1.0, 1.0, 1.0],
    )
    feasible_rate = 0.05464
    # Directly evaluate the model formula so this witness does not call the
    # production prediction helper under review.
    feasible_objective = math.fsum(
        (-math.expm1(-feasible_rate * time) - value) ** 2
        for time, value in zip(times, observed, strict=True)
    )

    assert result["optimization_converged"] is True
    assert result["status"] == "CALCULATED_REFERENCE_ONLY"
    assert result["objective"] <= feasible_objective + 1e-10
    assert (
        result["global_objective_gap_fraction"]
        <= result["global_objective_tolerance_fraction"]
    )
    assert result["global_search_iterations"] <= result["global_search_iteration_budget"]
    assert result["scientific_approval"] == "NOT_EVALUATED"


def test_multipeak_fit_holds_when_global_search_budget_is_exhausted() -> None:
    times = [0.11625890971846743, 12.249747272130165, 21.830648874490496]
    observed = [0.3524257328950935, 0.3685787023335362, 0.8036058964092736]
    result = fit_first_order_rate(
        times,
        observed,
        lower_s=0.0,
        upper_s=2.0,
        global_search_iterations=16,
    )

    assert result["optimization_converged"] is False
    assert result["status"] == "HOLD"
    assert result["identifiable"] is True
    assert result["global_objective_gap_fraction"] > result["global_objective_tolerance_fraction"]
    assert result["global_search_iterations"] == 16


def test_weighted_zero_time_and_boundary_fits_close_the_objective_gap() -> None:
    times = [0.0, 1.0, 2.0, 5.0]
    observed = first_order_conversion(times, 0.1)
    weighted = fit_first_order_rate(
        times, observed, lower_s=0.0, upper_s=1.0, weights=[1.0, 2.0, 3.0, 4.0]
    )
    assert weighted["optimization_converged"] is True
    assert weighted["rate_constant_s"] == pytest.approx(0.1, abs=1e-8)

    lower_boundary = fit_first_order_rate([1.0, 2.0, 3.0], [0.0, 0.0, 0.0], upper_s=2.0)
    upper_boundary = fit_first_order_rate([1.0, 2.0, 3.0], [1.0, 1.0, 1.0], upper_s=2.0)
    assert lower_boundary["optimization_converged"] is True
    assert lower_boundary["rate_constant_s"] == 0.0
    assert upper_boundary["optimization_converged"] is True
    assert upper_boundary["rate_constant_s"] == 2.0


def test_objective_interval_lower_bound_stays_below_sampled_values() -> None:
    rng = np.random.default_rng(731)
    for _ in range(20):
        times = rng.choice([0.0, 1e-3, 0.1, 1.0, 10.0, 100.0], size=5)
        observed = rng.uniform(0.0, 1.0, size=5)
        weights = rng.lognormal(0.0, 2.0, size=5)
        normalized_weights = weights / np.max(weights)
        weight_sum = float(np.sum(normalized_weights))
        lower = float(rng.uniform(0.0, 2.0))
        upper = float(rng.uniform(lower, 5.0))
        bound = _first_order_objective_interval_lower_bound(
            times, observed, normalized_weights, weight_sum, lower, upper
        )
        sampled = [
            float(
                np.sum(
                    normalized_weights
                    * (first_order_conversion(times, rate) - observed) ** 2
                )
            )
            for rate in np.linspace(lower, upper, 21)
        ]
        assert bound <= min(sampled) + 1e-12


@pytest.mark.parametrize("time_scale", [1e-200, 1.0, 1e200])
def test_objective_interval_bound_survives_inverse_time_rate_scaling(time_scale: float) -> None:
    base_times = np.array([0.11625890971846743, 12.249747272130165, 21.830648874490496])
    observed = np.array([0.3524257328950935, 0.3685787023335362, 0.8036058964092736])
    times = base_times * time_scale
    upper_rate = 2.0 / time_scale
    weights = np.ones_like(times)
    feasible_rate = 0.05464 / time_scale
    normalized_weights = weights / np.max(weights)
    bound = _first_order_objective_interval_lower_bound(
        times, observed, normalized_weights, 3.0, 0.0, upper_rate
    )
    feasible_objective = float(
        np.sum(normalized_weights * (first_order_conversion(times, feasible_rate) - observed) ** 2)
    )

    assert bound <= feasible_objective + 1e-12


@pytest.mark.parametrize("time_scale", [1e-200, 1e200])
def test_extreme_time_scaling_preserves_fit_gap_and_holds_unrepresentable_information(
    time_scale: float,
) -> None:
    base_times = [0.11625890971846743, 12.249747272130165, 21.830648874490496]
    observed = [0.3524257328950935, 0.3685787023335362, 0.8036058964092736]
    result = fit_first_order_rate(
        [time * time_scale for time in base_times],
        observed,
        lower_s=0.0,
        upper_s=2.0 / time_scale,
    )

    assert result["optimization_converged"] is True
    assert result["rate_constant_s"] / (1.0 / time_scale) == pytest.approx(
        0.05463612, abs=1e-7
    )
    assert result["status"] == "HOLD"
    if time_scale == 1e200:
        assert result["information_scalar"] is None
        assert result["identifiable"] is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"global_search_iterations": True},
        {"global_search_iterations": -1},
        {"global_objective_tolerance_fraction": 0.0},
        {"global_objective_tolerance_fraction": float("nan")},
    ],
)
def test_global_search_controls_reject_invalid_values(kwargs) -> None:
    with pytest.raises(ValueError):
        fit_first_order_rate([1.0, 2.0], [0.2, 0.4], **kwargs)


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
