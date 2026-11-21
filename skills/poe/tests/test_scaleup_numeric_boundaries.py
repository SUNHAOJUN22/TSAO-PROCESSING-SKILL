"""Scale-up groups must preserve finite ratios and reject invalid decisions."""

from __future__ import annotations

import json

import pytest

from skills.poe.core import compare_similarity, dimensionless_groups


def unit_inputs() -> dict[str, float]:
    return {
        "density_kg_m3": 1.0,
        "velocity_m_s": 1.0,
        "length_m": 1.0,
        "dynamic_viscosity_Pa_s": 1.0,
        "heat_capacity_J_kg_K": 1.0,
        "thermal_conductivity_W_m_K": 1.0,
        "diffusivity_m2_s": 1.0,
        "reaction_time_s": 1.0,
        "mixing_time_s": 1.0,
    }


@pytest.mark.parametrize("scale", [1e-300, 1.0, 1e308])
def test_dimensionless_groups_preserve_cancelling_material_scales(scale: float) -> None:
    inputs = unit_inputs()
    inputs.update(
        density_kg_m3=scale,
        dynamic_viscosity_Pa_s=scale,
        thermal_conductivity_W_m_K=scale,
        velocity_m_s=2.0,
        diffusivity_m2_s=2.0,
    )
    groups = dimensionless_groups(**inputs)
    assert groups == {
        "status": "CALCULATED_REFERENCE_ONLY",
        "Re": 2.0,
        "Pr": 1.0,
        "Sc": 0.5,
        "Pe_mass": 1.0,
        "Da_mixing": 1.0,
    }
    json.dumps(groups, allow_nan=False)


def test_dimensionless_groups_preserve_ratios_after_intermediate_underflow() -> None:
    groups = dimensionless_groups(
        **(
            unit_inputs()
            | {
                "density_kg_m3": 1e-300,
                "dynamic_viscosity_Pa_s": 1e-300,
                "thermal_conductivity_W_m_K": 1e-300,
                "velocity_m_s": 1e-100,
                "diffusivity_m2_s": 1e-100,
            }
        )
    )
    assert groups["Re"] == pytest.approx(1e-100, abs=0)
    assert groups["Sc"] == pytest.approx(1e100)
    assert groups["Pr"] == groups["Pe_mass"] == groups["Da_mixing"] == 1.0


@pytest.mark.parametrize(
    "updates",
    [
        {"density_kg_m3": 1e308, "velocity_m_s": 2.0},
        {"density_kg_m3": 1e-300, "velocity_m_s": 1e-100},
        {"density_kg_m3": 1e-300, "diffusivity_m2_s": 1e-100},
        {"density_kg_m3": 1e308, "diffusivity_m2_s": 2.0, "dynamic_viscosity_Pa_s": 1e-300},
    ],
)
def test_dimensionless_groups_reject_unrepresentable_positive_results(updates: dict) -> None:
    with pytest.raises(ValueError):
        dimensionless_groups(**(unit_inputs() | updates))


@pytest.mark.parametrize("field", list(unit_inputs()))
def test_dimensionless_groups_reject_boolean_inputs(field: str) -> None:
    with pytest.raises(ValueError):
        dimensionless_groups(**(unit_inputs() | {field: True}))


@pytest.mark.parametrize("field", ["base", "candidate", "tolerance"])
@pytest.mark.parametrize(
    "invalid", [True, "not-a-number", 10**400], ids=["boolean", "text", "overflowing-int"]
)
def test_similarity_invalid_numbers_return_structured_failure(field: str, invalid: object) -> None:
    values = {"base": 1.0, "candidate": 1.0, "tolerance": 0.1}
    values[field] = invalid
    result = compare_similarity(
        {"Re": values["base"]}, {"Re": values["candidate"]}, {"Re": values["tolerance"]}
    )
    assert result["status"] == "FAIL"
    assert result["deviations_fraction"] == {}
    assert result["issues"]
    json.dumps(result, allow_nan=False)


def test_similarity_unrepresentable_deviation_does_not_emit_infinity() -> None:
    result = compare_similarity({"Re": 1e-300}, {"Re": 1e308}, {"Re": 0.1})
    assert result["status"] == "FAIL"
    assert result["deviations_fraction"] == {}
    json.dumps(result, allow_nan=False)


def test_similarity_preserves_equal_large_values_and_declared_tolerance() -> None:
    assert compare_similarity({"Re": 1e308}, {"Re": 1e308}, {"Re": 0.0})["status"] == "PASS"
    allowed = compare_similarity({"Re": 1e308}, {"Re": 1.5e308}, {"Re": 0.5})
    assert allowed["status"] == "PASS"
    assert allowed["deviations_fraction"]["Re"] == 0.5
    assert compare_similarity({"Re": 1e308}, {"Re": 1.5e308}, {"Re": 0.49})["status"] == "FAIL"
    assert compare_similarity({"Re": 1.0}, {"Re": 1.0}, {})["status"] == "HOLD"
