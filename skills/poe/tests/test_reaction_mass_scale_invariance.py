from __future__ import annotations

import pytest

from skills.poe.material_balance import evaluate_material_balance
from skills.poe.tests.test_material_balance_v2 import base_case, quantity


def reaction_case(scale: float, *, balanced: bool) -> dict:
    case = base_case()
    product_weight = 10.0 if balanced else 20.0
    case["molecular_weights_g_mol"] = {"A": 10.0, "B": product_weight}
    case["streams"][0]["flow"] = quantity(0.01, "kg/s", "mass")
    case["streams"][1]["flow"] = quantity(product_weight / 1000.0, "kg/s", "mass")
    case["streams"][1]["composition"] = {"A": 0.0, "B": 1.0}
    case["reactions"] = [
        {
            "reaction_id": "A-TO-B",
            "stoichiometry": {"A": -scale, "B": scale},
            "extent": quantity(1.0 / scale, "mol/s", "molar"),
        }
    ]
    return case


@pytest.mark.parametrize("scale", [1.0, 1e-20, 1e-100, 1e-300, 1e300, 1e308])
def test_mass_inconsistency_cannot_be_hidden_by_reaction_normalization(scale: float) -> None:
    result = evaluate_material_balance(reaction_case(scale, balanced=False))
    assert result["status"] == "FAIL"
    assert any("not mass-consistent" in error for error in result["errors"])


@pytest.mark.parametrize("scale", [1.0, 1e-20, 1e-100, 1e-300, 1e300, 1e308])
def test_balanced_reaction_is_invariant_under_reciprocal_extent_scaling(scale: float) -> None:
    result = evaluate_material_balance(reaction_case(scale, balanced=True))
    assert result["status"] == "PASS", result["errors"]
    assert result["total"]["incoming"] == pytest.approx(0.01)
    assert result["total"]["outgoing"] == pytest.approx(0.01)
