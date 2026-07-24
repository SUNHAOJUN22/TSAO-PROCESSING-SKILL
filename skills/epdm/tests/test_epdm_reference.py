from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from skills.epdm.core import (
    EpdmKineticParameters, EpdmKineticState, active_site_fraction, architecture_metrics,
    devolatilization_residual, grade_transition_offspec_fraction, heat_removal_margin,
    insertion_fractions, mixing_reynolds, mooney_reference, recycle_poison_steady_state,
    validate_epdm_case,
)

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    return json.loads((ROOT / "fixtures/reference_cases.json").read_text(encoding="utf-8"))["valid_case"]


def test_active_site_fraction_and_invalid_anchor():
    assert active_site_fraction(10.0, 6.0) == pytest.approx(0.6)
    with pytest.raises(ValueError): active_site_fraction(1.0, 2.0)


def test_ternary_insertion_and_architecture_metrics():
    state = EpdmKineticState(1.2, 1.0, 0.04, 0.001, 1e-6)
    params = EpdmKineticParameters(2.0, 1.6, 0.5, 0.08, 0.02, 10.0)
    fractions = insertion_fractions(state, params)
    assert sum(fractions.values()) == pytest.approx(1.0)
    metrics = architecture_metrics(state, params, secondary_diene_insertion_probability=0.05, branch_efficiency=0.5, gel_critical_branch_index=1.0)
    assert 0 <= metrics["gel_risk_index"] <= 1
    assert metrics["retained_unsaturation_fraction"] > 0


def test_process_references_known_solutions():
    assert heat_removal_margin(80, 100) == pytest.approx(0.2)
    assert mixing_reynolds(800, 2, 1, 4) == pytest.approx(400)
    assert recycle_poison_steady_state(1.0, 0.8, 0.1, 0.5) == pytest.approx(1/(1-0.36))
    assert devolatilization_residual(0.1, 0.2, 5) == pytest.approx(0.1 * math.exp(-1))
    assert grade_transition_offspec_fraction(100, 25) == pytest.approx(0.2)
    assert mooney_reference(200, 0.1, 20) > 0


def test_valid_case_passes_software_gate():
    result = validate_epdm_case(fixture())
    assert result["status"] == "PASS"
    assert result["scientific_technical_approval"] == "NOT_EVALUATED"


def test_missing_benchmark_and_customer_bridge_hold():
    data = fixture(); data["catalyst"]["vanadium_benchmark"] = False; data["product_bridge"].pop("customer_line")
    result = validate_epdm_case(data)
    assert result["status"] == "HOLD"


def test_active_site_and_heat_capacity_fail():
    data = fixture(); data["catalyst"]["active_site_mol"] = 1.0; data["reactor"]["heat_removal_capacity_kW"] = 40.0
    assert validate_epdm_case(data)["status"] == "FAIL"


def test_unmeasured_topology_and_equilibrium_devolatilization_hold():
    data = fixture(); data["monomers"]["diene_topology_measured"] = False; data["recovery"]["non_equilibrium_devolatilization"] = False
    assert validate_epdm_case(data)["status"] == "HOLD"
