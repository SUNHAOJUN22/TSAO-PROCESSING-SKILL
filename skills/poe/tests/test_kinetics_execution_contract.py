from __future__ import annotations

import math
from dataclasses import asdict

import pytest

from skills.poe.kinetics import (
    KineticParameters,
    KineticState,
    _state_add_vector,
    simulate_kinetics,
    simulate_kinetics_terminal,
)

SOLVERS = (simulate_kinetics, simulate_kinetics_terminal)


@pytest.mark.parametrize("solver", SOLVERS)
@pytest.mark.parametrize("duration", [1.0, 1e-16])
def test_rescaled_decay_reaches_analytic_solution(solver, duration: float) -> None:
    # dD/dt = -kD has the independent solution D(t) = D(0) exp(-kt).
    initial = KineticState(1.0, 0.0, 1.0)
    parameters = KineticParameters(0.0, 0.0, 0.0, 0.0, 1.0 / duration)
    result = solver(initial, parameters, duration, duration / 100.0)
    assert result["final"]["dormant_sites"] == pytest.approx(math.exp(-1.0), abs=4e-11)
    assert result["scientific_approval"] == "NOT_EVALUATED"
    if "history" in result:
        times = [row["time_s"] for row in result["history"]]
        assert times[-1] == duration
        assert all(left < right for left, right in zip(times[:-1], times[1:], strict=True))


def test_short_final_step_is_integrated_not_discarded() -> None:
    duration = 5e-16
    initial = KineticState(1.0, 0.0, 1.0)
    parameters = KineticParameters(0.0, 0.0, 0.0, 0.0, 1e15)
    result = simulate_kinetics(initial, parameters, duration, 2e-16)
    assert result["history"][-1]["time_s"] == duration
    assert len(result["history"]) == 4
    assert result["final"]["dormant_sites"] == pytest.approx(math.exp(-0.5), abs=4e-6)


@pytest.mark.parametrize("solver", SOLVERS)
def test_zero_duration_remains_an_exact_noop(solver) -> None:
    initial = KineticState(1.2, 0.8, 0.01)
    parameters = KineticParameters(0.002, 0.08, 0.05, 0.003, 0.0005)
    result = solver(initial, parameters, 0.0, 0.01)
    assert result["final"] == asdict(initial)
    assert result["metrics"]["mass_balance_residual_mol_L"] == 0.0


@pytest.mark.parametrize("solver", SOLVERS)
def test_finite_inputs_with_nonfinite_stages_do_not_publish_a_result(solver) -> None:
    # The intermediate product k_init * dormant overflows before multiplication
    # by zero. Previously NaN was clipped to zero and erased the entire state.
    initial = KineticState(0.0, 0.0, 1e308)
    parameters = KineticParameters(1e308, 0.0, 0.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="non-finite"):
        solver(initial, parameters, 1.0, 0.1)


@pytest.mark.parametrize("invalid", [math.nan, math.inf])
def test_stage_guard_rejects_nonfinite_values_before_clipping(invalid: float) -> None:
    state = (0.0,) * 11
    derivative = (invalid,) + (0.0,) * 10
    with pytest.raises(ValueError, match="non-finite monomer_a"):
        _state_add_vector(state, derivative, 1.0)


def test_existing_negative_state_tolerance_is_not_relaxed() -> None:
    state = (0.0,) * 11
    with pytest.raises(ValueError, match="materially negative"):
        _state_add_vector(state, (-1e-9,) + (0.0,) * 10, 1.0)
    assert _state_add_vector(state, (-5e-11,) + (0.0,) * 10, 1.0) == state


def test_full_and_terminal_preserve_each_monomer_inventory() -> None:
    initial = KineticState(1.2, 0.8, 0.01)
    parameters = KineticParameters(0.002, 0.08, 0.05, 0.003, 0.0005)
    full = simulate_kinetics(initial, parameters, 10.0, 0.01)
    terminal = simulate_kinetics_terminal(initial, parameters, 10.0, 0.01)
    assert full["final"] == terminal["final"]
    assert full["metrics"] == terminal["metrics"]
    final = full["final"]
    # Independent elemental-unit accounting, not the implementation's combined residual.
    assert final["monomer_a"] + final["live_a_units"] + final["dead_a_units"] == pytest.approx(
        initial.monomer_a, abs=1e-12
    )
    assert final["monomer_b"] + final["live_b_units"] + final["dead_b_units"] == pytest.approx(
        initial.monomer_b, abs=1e-12
    )
    assert full["history"][-1]["time_s"] == 10.0


def test_rescaled_decay_retains_fourth_order_convergence() -> None:
    duration = 1e-16
    initial = KineticState(1.0, 0.0, 1.0)
    parameters = KineticParameters(0.0, 0.0, 0.0, 0.0, 1.0 / duration)
    errors = []
    for steps in (25, 50):
        result = simulate_kinetics_terminal(initial, parameters, duration, duration / steps)
        errors.append(abs(result["final"]["dormant_sites"] - math.exp(-1.0)))
    assert errors[1] < 1e-9
    assert 15.0 < errors[0] / errors[1] < 17.0
