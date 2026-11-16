from __future__ import annotations

import math

import pytest

from skills.epdm.kinetics import (
    EpdmActivationEnergies,
    EpdmKineticParameters,
    arrhenius_rate_constant,
    temperature_adjusted_parameters,
)


@pytest.mark.parametrize("temperature", [math.ulp(0.0), 1e-310, 298.15, 1e308])
def test_zero_activation_preserves_reference_rate(temperature: float) -> None:
    assert arrhenius_rate_constant(2.5, 0.0, temperature) == 2.5


@pytest.mark.parametrize("temperature", [math.ulp(0.0), 1e-310, 298.15, 1e308])
def test_equal_temperature_preserves_reference_rate(temperature: float) -> None:
    assert arrhenius_rate_constant(2.5, 100.0, temperature, temperature) == 2.5


def test_indeterminate_inverse_temperatures_raise_a_domain_error() -> None:
    with pytest.raises(ValueError, match="Arrhenius exponent became non-finite"):
        arrhenius_rate_constant(1.0, 100.0, math.ulp(0.0), 2.0 * math.ulp(0.0))


def test_parameter_bundle_preserves_identity_at_reference_temperature() -> None:
    parameters = EpdmKineticParameters(2.0, 1.6, 0.5, 0.08, 0.02, 10.0)
    energies = EpdmActivationEnergies(100.0, 200.0, 300.0, 400.0, 500.0, 600.0)
    assert temperature_adjusted_parameters(
        parameters, energies, math.ulp(0.0), math.ulp(0.0)
    ) == parameters


@pytest.mark.parametrize("temperature", [math.ulp(0.0), 1e-310, 298.15, 1e308])
def test_zero_activation_bundle_is_temperature_independent(temperature: float) -> None:
    parameters = EpdmKineticParameters(2.0, 1.6, 0.5, 0.08, 0.02, 10.0)
    energies = EpdmActivationEnergies(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    assert temperature_adjusted_parameters(parameters, energies, temperature) == parameters
