from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

import skills.epdm.core as epdm_core
from skills.epdm.core import (
    EpdmActivationEnergies,
    EpdmKineticParameters,
    EpdmKineticState,
    SemibatchFeed,
    SemibatchInventory,
    architecture_metrics,
    insertion_fractions,
    insertion_rates,
    semibatch_material_energy_step,
    three_level_kinetic_suite,
    validate_epdm_case,
)
from skills.epdm.package_audit import audit_epdm_process_package

ROOT = Path(__file__).resolve().parents[1]


def _reference_cases() -> dict[str, object]:
    return json.loads((ROOT / "fixtures/reference_cases.json").read_text(encoding="utf-8"))


def _golden() -> dict[str, object]:
    return json.loads((ROOT / "fixtures/v1_golden_outputs.json").read_text(encoding="utf-8"))


def test_v1_public_api_and_return_envelopes_are_locked():
    contract = json.loads((ROOT / "fixtures/v1_api_contract.json").read_text(encoding="utf-8"))
    assert epdm_core.__all__ == contract["public_names"]

    case_result = validate_epdm_case(_reference_cases()["valid_case"])
    assert set(case_result) >= set(contract["return_envelopes"]["validate_epdm_case"])

    semibatch_result = semibatch_material_energy_step(
        SemibatchInventory(100.0, 120.0, 100.0, 4.0, 0.0, 323.15, 900.0),
        SemibatchFeed(0.08, 0.06, 0.002, 0.01),
        EpdmKineticParameters(2.0, 1.6, 0.5, 0.08, 0.02, 10.0),
        active_site_mol_L=0.001,
        poison_mol_L=1e-6,
        step_s=30.0,
        reaction_enthalpy_kJ_mol=85.0,
        heat_removal_kW=7.0,
    )
    assert set(semibatch_result) == set(
        contract["return_envelopes"]["semibatch_material_energy_step"]
    )

    suite = three_level_kinetic_suite(
        EpdmKineticState(1.2, 1.0, 0.04, 0.001, 1e-6),
        EpdmKineticParameters(2.0, 1.6, 0.5, 0.08, 0.02, 10.0),
        EpdmActivationEnergies(35_000, 37_000, 42_000, 28_000, 45_000, 20_000),
        temperature_K=323.15,
        residence_time_s=300.0,
    )
    assert set(suite) == set(contract["return_envelopes"]["three_level_kinetic_suite"])


def test_v1_golden_numerics_are_unchanged():
    golden = _golden()
    relative = golden["tolerance"]["relative"]
    absolute = golden["tolerance"]["absolute"]
    state = EpdmKineticState(*golden["reference_input"]["state"])
    parameters = EpdmKineticParameters(*golden["reference_input"]["parameters"])

    assert insertion_rates(state, parameters) == pytest.approx(
        golden["insertion_rates"], rel=relative, abs=absolute
    )
    assert insertion_fractions(state, parameters) == pytest.approx(
        golden["insertion_fractions"], rel=relative, abs=absolute
    )
    assert architecture_metrics(
        state,
        parameters,
        secondary_diene_insertion_probability=0.05,
        branch_efficiency=0.5,
        gel_critical_branch_index=1.0,
    ) == pytest.approx(golden["architecture"], rel=relative, abs=absolute)


def test_variable_volume_semibatch_golden_output_is_locked():
    inventory = SemibatchInventory(100.0, 120.0, 100.0, 4.0, 0.0, 323.15, 900.0)
    feed = SemibatchFeed(0.08, 0.06, 0.002, 0.01)
    parameters = EpdmKineticParameters(2.0, 1.6, 0.5, 0.08, 0.02, 10.0)
    result = semibatch_material_energy_step(
        inventory,
        feed,
        parameters,
        active_site_mol_L=0.001,
        poison_mol_L=1e-6,
        step_s=30.0,
        reaction_enthalpy_kJ_mol=85.0,
        heat_removal_kW=7.0,
    )
    golden = _golden()["semibatch_reference"]
    assert result["polymer_increment_mol"] == pytest.approx(golden["polymer_increment_mol"])
    assert result["molar_closure_residual"] == pytest.approx(
        golden["molar_closure_residual"], abs=1e-12
    )
    assert result["inventory"] == pytest.approx(golden["inventory"])


def test_malformed_nested_sections_fail_closed_without_exception_leak():
    base = _reference_cases()["valid_case"]
    for section in (
        "catalyst",
        "monomers",
        "kinetics",
        "impurities",
        "reactor",
        "recovery",
        "product_bridge",
    ):
        payload = copy.deepcopy(base)
        payload[section] = []
        result = validate_epdm_case(payload)
        assert result["status"] == "FAIL"
        assert result["pass"] is False
        assert result["errors"]


def test_parameter_provenance_is_a_runtime_hold():
    payload = copy.deepcopy(_reference_cases()["valid_case"])
    payload["kinetics"].pop("parameter_basis")
    payload["kinetics"].pop("parameter_evidence_ids")
    result = validate_epdm_case(payload)
    assert result["status"] == "HOLD"
    assert any("parameter basis" in item for item in result["holds"])
    assert any("parameters are not anchored" in item for item in result["holds"])

    payload = copy.deepcopy(_reference_cases()["valid_case"])
    payload.pop("case_kind")
    result = validate_epdm_case(payload)
    assert result["status"] == "HOLD"
    assert any("software fixture" in item for item in result["holds"])


def test_case_schema_validates_fixture_and_rejects_malformed_instance():
    schema = json.loads((ROOT / "schemas/epdm_case.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    valid = _reference_cases()["valid_case"]
    assert not list(validator.iter_errors(valid))

    invalid = copy.deepcopy(valid)
    invalid["reactor"] = []
    assert list(validator.iter_errors(invalid))


def test_recursive_evidence_audit_catches_parameter_evidence_and_duplicates():
    package = copy.deepcopy(_reference_cases()["valid_package"])
    package["evidence_ledger"] = [
        item for item in package["evidence_ledger"] if item["evidence_id"] != "E-KINETICS"
    ]
    result = audit_epdm_process_package(package)
    assert result["status"] == "FAIL"
    assert any("E-KINETICS" in item for item in result["errors"])

    package = copy.deepcopy(_reference_cases()["valid_package"])
    package["evidence_ledger"].append(copy.deepcopy(package["evidence_ledger"][0]))
    result = audit_epdm_process_package(package)
    assert result["status"] == "FAIL"
    assert any("duplicate IDs" in item for item in result["errors"])


def test_package_schema_resolves_case_schema_and_validates_fixture():
    case_schema = json.loads((ROOT / "schemas/epdm_case.schema.json").read_text(encoding="utf-8"))
    package_schema = json.loads(
        (ROOT / "schemas/epdm_package.schema.json").read_text(encoding="utf-8")
    )
    registry = Registry().with_resource(
        case_schema["$id"], Resource.from_contents(case_schema)
    )
    validator = Draft202012Validator(package_schema, registry=registry)
    assert not list(validator.iter_errors(_reference_cases()["valid_package"]))


def test_package_audit_malformed_nested_payload_fails_closed():
    package = copy.deepcopy(_reference_cases()["valid_package"])
    package["evidence_ledger"] = None
    result = audit_epdm_process_package(package)
    assert result["status"] == "FAIL"
    assert result["errors"]
