"""Independent closed forms for the additional POE chain-mass moments."""

from __future__ import annotations

import math

import pytest

from skills.poe.kinetics import (
    KineticParameters,
    KineticState,
    simulate_kinetics,
    simulate_kinetics_terminal,
)


@pytest.mark.parametrize("solver", [simulate_kinetics, simulate_kinetics_terminal])
def test_copolymer_mass_moments_match_independent_compound_poisson_solution(solver):
    # With a fixed population C and no initiation/loss, each chain receives
    # independent A/B insertions. A(t)=A0 exp(-ka*C*t), with Poisson mean
    # uA=(A0-A(t))/C, and likewise B. Var(M) grows by Ma^2*uA+Mb^2*uB.
    params = KineticParameters(0.0, 0.08, 0.05, 0.0, 0.0)
    ma, mb, chains, time = params.molar_mass_a, params.molar_mass_b, 0.2, 3.0
    initial = KineticState(
        1.2,
        0.8,
        0.0,
        live_chains=chains,
        live_a_units=chains,
        live_b_units=chains,
        live_second_moment=4 * chains,
        live_mass_second_moment=0.5 * chains * ((2 * ma) ** 2 + (2 * mb) ** 2),
    )
    result = solver(initial, params, time, 0.01)
    final = result["final"]
    a = initial.monomer_a * math.exp(-params.k_prop_a * chains * time)
    b = initial.monomer_b * math.exp(-params.k_prop_b * chains * time)
    ua, ub = (initial.monomer_a - a) / chains, (initial.monomer_b - b) / chains
    mean = ma + mb + ma * ua + mb * ub
    variance = (ma - mb) ** 2 + ma**2 * ua + mb**2 * ub
    expected_mass_second = chains * (mean**2 + variance)
    assert final["monomer_a"] == pytest.approx(a, rel=1e-12)
    assert final["monomer_b"] == pytest.approx(b, rel=1e-12)
    assert final["live_mass_second_moment"] == pytest.approx(expected_mass_second, rel=1e-12)
    assert result["metrics"]["number_average_molar_mass_g_mol"] == pytest.approx(mean, rel=1e-12)
    assert result["metrics"]["weight_average_molar_mass_g_mol"] == pytest.approx(
        mean + variance / mean, rel=1e-12
    )
    assert abs(result["metrics"]["mass_balance_residual_mol_L"]) < 1e-12
    assert result["scientific_approval"] == "NOT_EVALUATED"


@pytest.mark.parametrize("solver", [simulate_kinetics, simulate_kinetics_terminal])
def test_transfer_conserves_total_mass_moment_with_exponential_population_loss(solver):
    params = KineticParameters(0.0, 0.0, 0.0, 0.1, 0.0)
    initial = KineticState(
        0.0,
        0.0,
        0.0,
        live_chains=0.2,
        live_a_units=0.4,
        live_second_moment=0.8,
        live_mass_second_moment=0.8 * params.molar_mass_a**2,
    )
    result = solver(initial, params, 2.0, 0.01)
    final = result["final"]
    survival = math.exp(-0.2)
    assert final["live_mass_second_moment"] == pytest.approx(
        initial.live_mass_second_moment * survival, rel=1e-12
    )
    assert final["dead_mass_second_moment"] == pytest.approx(
        initial.live_mass_second_moment * (1 - survival), rel=1e-12
    )
    assert result["metrics"]["weight_average_molar_mass_g_mol"] == pytest.approx(
        2 * params.molar_mass_a, rel=1e-12
    )
