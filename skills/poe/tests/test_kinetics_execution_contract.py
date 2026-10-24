from __future__ import annotations

import json
import math
from dataclasses import asdict

import pytest

from skills.poe.kinetics import (
    KineticParameters,
    KineticState,
    _state_add_vector,
    kinetic_derivative,
    kinetic_metrics,
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
    expected = asdict(initial)
    expected["live_mass_second_moment"] = 0.0
    expected["dead_mass_second_moment"] = 0.0
    assert result["final"] == expected
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
    state = (0.0,) * 13
    derivative = (invalid,) + (0.0,) * 12
    with pytest.raises(ValueError, match="non-finite monomer_a"):
        _state_add_vector(state, derivative, 1.0)


def test_existing_negative_state_tolerance_is_not_relaxed() -> None:
    state = (0.0,) * 13
    with pytest.raises(ValueError, match="materially negative"):
        _state_add_vector(state, (-1e-9,) + (0.0,) * 12, 1.0)
    assert _state_add_vector(state, (-5e-11,) + (0.0,) * 12, 1.0) == state


def test_boolean_state_and_parameter_inputs_are_rejected() -> None:
    with pytest.raises(ValueError, match="monomer_a must be finite"):
        KineticState(True, 0.0, 0.0).validate()
    with pytest.raises(ValueError, match="k_init must be finite"):
        KineticParameters(True, 0.0, 0.0, 0.0, 0.0).validate()


@pytest.mark.parametrize("solver", SOLVERS)
@pytest.mark.parametrize("duration,step", [(True, 0.1), (1.0, True)])
def test_boolean_time_inputs_are_rejected(solver, duration, step) -> None:
    with pytest.raises(ValueError, match="must be a finite real number"):
        solver(
            KineticState(1.0, 0.0, 0.01),
            KineticParameters(0.0, 0.0, 0.0, 0.0, 0.0),
            duration,
            step,
        )


def test_public_derivative_rejects_nonfinite_arithmetic() -> None:
    state = KineticState(0.0, 0.0, 1e308)
    parameters = KineticParameters(1e308, 0.0, 0.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="kinetic derivative.*non-finite"):
        kinetic_derivative(state, parameters)


def test_weight_average_molar_mass_uses_chain_mass_distribution() -> None:
    parameters = KineticParameters(0.0, 0.0, 0.0, 0.0, 0.0)
    mass_a = parameters.molar_mass_a
    mass_b = parameters.molar_mass_b
    # Both populations have N=2, A=B=2 units, and DP second moment=8.
    # Their chain-mass distributions differ: AA + BB versus AB + AB.
    aa_and_bb = KineticState(
        0.0,
        0.0,
        0.0,
        live_chains=2.0,
        live_a_units=2.0,
        live_b_units=2.0,
        live_second_moment=8.0,
        live_mass_second_moment=(2.0 * mass_a) ** 2 + (2.0 * mass_b) ** 2,
    )
    ab_and_ab = KineticState(
        0.0,
        0.0,
        0.0,
        live_chains=2.0,
        live_a_units=2.0,
        live_b_units=2.0,
        live_second_moment=8.0,
        live_mass_second_moment=2.0 * (mass_a + mass_b) ** 2,
    )

    aa_bb_metrics = kinetic_metrics(aa_and_bb, aa_and_bb, parameters)
    ab_ab_metrics = kinetic_metrics(ab_and_ab, ab_and_ab, parameters)
    assert aa_bb_metrics["weight_average_molar_mass_g_mol"] == pytest.approx(
        ((2.0 * mass_a) ** 2 + (2.0 * mass_b) ** 2) / (2.0 * mass_a + 2.0 * mass_b)
    )
    assert ab_ab_metrics["weight_average_molar_mass_g_mol"] == pytest.approx(mass_a + mass_b)
    assert aa_bb_metrics["weight_average_molar_mass_g_mol"] != pytest.approx(
        ab_ab_metrics["weight_average_molar_mass_g_mol"]
    )


def test_preexisting_chains_require_their_mass_moment() -> None:
    state = KineticState(0.0, 0.0, 0.0, live_chains=1.0, live_a_units=1.0)
    with pytest.raises(ValueError, match="live_mass_second_moment is required"):
        simulate_kinetics(
            state,
            KineticParameters(0.0, 0.0, 0.0, 0.0, 0.0),
            duration_s=0.0,
            step_s=1.0,
        )


@pytest.mark.parametrize("population", ["live", "dead"])
def test_seeded_mass_second_moment_respects_the_cauchy_lower_bound(population: str) -> None:
    parameters = KineticParameters(0.0, 0.0, 0.0, 0.0, 0.0)
    invalid_values = {
        "monomer_a": 0.0,
        "monomer_b": 0.0,
        "dormant_sites": 0.0,
        f"{population}_chains": 1.0,
        f"{population}_a_units": 1.0,
        f"{population}_mass_second_moment": 1.0,
    }
    invalid = KineticState(**invalid_values)
    with pytest.raises(ValueError, match="below the minimum implied"):
        simulate_kinetics(invalid, parameters, duration_s=0.0, step_s=1.0)

    monodisperse_values = {
        **invalid_values,
        f"{population}_second_moment": 1.0,
        f"{population}_mass_second_moment": parameters.molar_mass_a**2,
    }
    monodisperse = KineticState(**monodisperse_values)
    assert kinetic_metrics(monodisperse, monodisperse, parameters)[
        "weight_average_molar_mass_g_mol"
    ] == pytest.approx(parameters.molar_mass_a)


def test_nonempty_chain_without_repeat_units_is_rejected() -> None:
    state = KineticState(
        0.0,
        0.0,
        0.0,
        live_chains=1.0,
        live_mass_second_moment=0.0,
    )
    with pytest.raises(ValueError, match="polymer units are required"):
        simulate_kinetics(
            state,
            KineticParameters(0.0, 0.0, 0.0, 0.0, 0.0),
            duration_s=0.0,
            step_s=1.0,
        )


def test_live_mass_moment_derivative_tracks_propagation_and_chain_loss() -> None:
    mass_a = 28.05
    mass_b = 112.22
    mass_moment = 40_000.0
    state = KineticState(
        monomer_a=1.0,
        monomer_b=0.5,
        dormant_sites=0.0,
        live_chains=2.0,
        live_a_units=2.0,
        live_b_units=2.0,
        live_mass_second_moment=mass_moment,
    )
    parameters = KineticParameters(0.0, 0.1, 0.2, 0.03, 0.02, mass_a, mass_b)
    derivative = kinetic_derivative(state, parameters)
    average_chain_mass = (2.0 * mass_a + 2.0 * mass_b) / 2.0
    propagation_a = 0.1 * 1.0 * 2.0
    propagation_b = 0.2 * 0.5 * 2.0
    loss = (0.03 + 0.02) * 2.0
    expected_live = (
        propagation_a * (2.0 * mass_a * average_chain_mass + mass_a**2)
        + propagation_b * (2.0 * mass_b * average_chain_mass + mass_b**2)
        - loss * mass_moment / 2.0
    )
    assert derivative.live_mass_second_moment == pytest.approx(expected_live)
    assert derivative.dead_mass_second_moment == pytest.approx(loss * mass_moment / 2.0)


def test_live_mass_moment_derivative_tracks_initiation() -> None:
    parameters = KineticParameters(0.5, 0.0, 0.0, 0.0, 0.0)
    state = KineticState(1.0, 0.0, 0.2)
    derivative = kinetic_derivative(state, parameters)
    initiation_rate = parameters.k_init * state.dormant_sites * state.monomer_a
    assert derivative.live_mass_second_moment == pytest.approx(
        initiation_rate * parameters.molar_mass_a**2
    )


def test_large_noop_monomer_inventory_has_finite_conservation_metrics() -> None:
    initial = KineticState(1e308, 1e308, 0.0)
    result = simulate_kinetics(
        initial,
        KineticParameters(0.0, 0.0, 0.0, 0.0, 0.0),
        duration_s=0.0,
        step_s=0.1,
    )
    assert result["metrics"]["monomer_consumed_mol_L"] == 0.0
    assert result["metrics"]["mass_balance_residual_mol_L"] == 0.0
    json.dumps(result, allow_nan=False)


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
