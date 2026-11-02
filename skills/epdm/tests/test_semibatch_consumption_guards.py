from __future__ import annotations

import math

import pytest

from skills.epdm.kinetics import EpdmKineticParameters
from skills.epdm.process import (
    SemibatchFeed,
    SemibatchInventory,
    semibatch_material_energy_step,
    semibatch_trajectory,
)

SOLVERS = (semibatch_material_energy_step, semibatch_trajectory)
SPECIES = ("ethylene", "propylene", "diene")


@pytest.mark.parametrize("solver", SOLVERS)
@pytest.mark.parametrize("index", range(3))
def test_zero_duration_cannot_hide_a_nonfinite_consumption_demand(solver, index: int) -> None:
    amounts = [0.0] * 3
    propagation = [0.0] * 3
    amounts[index] = propagation[index] = 1e308
    # All input values and the derived rate are finite. The established
    # rate * volume * duration order overflows before multiplication by zero.
    # A max-based check used to hide a NaN in the second or third component and
    # publish complete conversion at zero duration with a zero closure residual.
    with pytest.raises(ValueError, match=f"{SPECIES[index]} consumption demand must be finite"):
        solver(
            SemibatchInventory(1e308, *amounts, 0.0, 300.0, 1e308),
            SemibatchFeed(0.0, 0.0, 0.0),
            EpdmKineticParameters(*propagation, 0.0, 0.0),
            active_site_mol_L=1.0,
            poison_mol_L=0.0,
            step_s=0.0,
            reaction_enthalpy_kJ_mol=0.0,
            heat_removal_kW=0.0,
            **({"steps": 1} if solver is semibatch_trajectory else {}),
        )


@pytest.mark.parametrize("solver", SOLVERS)
def test_zero_active_sites_cannot_hide_a_nonfinite_deactivation_rate(solver) -> None:
    with pytest.raises(ValueError, match="deactivation rate must be finite"):
        solver(
            SemibatchInventory(1.0, 1.0, 1.0, 1.0, 0.0, 300.0, 1.0),
            SemibatchFeed(0.0, 0.0, 0.0),
            EpdmKineticParameters(0.0, 0.0, 0.0, 0.0, 0.0, 1e308),
            active_site_mol_L=0.0,
            poison_mol_L=1e308,
            step_s=1.0,
            reaction_enthalpy_kJ_mol=0.0,
            heat_removal_kW=0.0,
            **({"steps": 1} if solver is semibatch_trajectory else {}),
        )


@pytest.mark.parametrize("propagation,expected", [(0.25, 0.25), (1.0, 1.0), (2.0, 1.0)])
def test_consumption_limits_preserve_each_species_and_scalar_trajectory_parity(
    propagation: float, expected: float
) -> None:
    inventory = SemibatchInventory(1.0, 1.0, 1.0, 1.0, 0.0, 300.0, 1.0)
    feed = SemibatchFeed(0.0, 0.0, 0.0)
    parameters = EpdmKineticParameters(propagation, propagation, propagation, 0.0, 0.0)
    options = dict(
        active_site_mol_L=1.0,
        poison_mol_L=0.0,
        step_s=1.0,
        reaction_enthalpy_kJ_mol=1.0,
        heat_removal_kW=0.0,
    )
    scalar = semibatch_material_energy_step(inventory, feed, parameters, **options)
    trajectory = semibatch_trajectory(inventory, feed, parameters, steps=1, **options)
    for name in SPECIES:
        assert scalar["consumed_mol"][name] == expected
        assert scalar["inventory"][f"{name}_mol"] + expected == 1.0
    assert scalar["polymer_increment_mol"] == 3.0 * expected
    assert scalar["molar_closure_residual"] == 0.0
    for name, value in scalar["inventory"].items():
        assert trajectory["final_inventory"][name].hex() == value.hex()


def test_consumption_zero_tie_keeps_the_available_inventory_sign() -> None:
    result = semibatch_material_energy_step(
        SemibatchInventory(1.0, -0.0, -0.0, -0.0, 0.0, 300.0, 1.0),
        SemibatchFeed(-0.0, -0.0, -0.0),
        EpdmKineticParameters(-0.0, -0.0, -0.0, 0.0, 0.0),
        active_site_mol_L=1.0,
        poison_mol_L=0.0,
        step_s=1.0,
        reaction_enthalpy_kJ_mol=1.0,
        heat_removal_kW=0.0,
    )
    # Demand is +0.0; min(available, demand) returns the first, -0.0 operand.
    for value in result["consumed_mol"].values():
        assert value == 0.0
        assert math.copysign(1.0, value) == -1.0
