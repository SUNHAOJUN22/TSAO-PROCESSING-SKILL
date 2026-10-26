from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from skills.epdm.canonical_loader import CanonicalProjectLoadError, load_canonical_project
from skills.epdm.contracts import ContractValidationError, GateDecision
from skills.epdm.executable_rhs import (
    build_calculated_reference_rate_package,
    execute_structural_rhs,
)
from skills.epdm.numerical_integration import build_integration_request, integrate_adaptive
from skills.epdm.reaction_network import audit_reaction_network, build_reaction_network
from skills.epdm.state_generator import generate_state_definition
from skills.epdm.validation_v2 import validate_v2_project


def _state():
    return generate_state_definition(
        source_state_definition_id="STATE-LAYOUT-IDENTITY",
        model_level=2,
        site_family_ids=("SITE-A",),
    )


def test_reordered_variables_cannot_retain_the_old_declared_indices():
    state = _state()
    variables = list(state.variables)
    variables[0], variables[1] = variables[1], variables[0]
    with pytest.raises(ContractValidationError, match="indices"):
        replace(state, variables=variables)


@pytest.mark.parametrize("index", [False, 0.0, 1, 20])
def test_state_indices_are_integer_vector_positions(index):
    state = _state()
    variables = (replace(state.variables[0], index=index),) + state.variables[1:]
    with pytest.raises(ContractValidationError, match="indices"):
        replace(state, variables=variables)


def test_state_definition_owns_input_sequences_before_caching_or_network_building():
    original = _state()
    variables = list(original.variables)
    sites = list(original.site_family_ids)
    terminals = list(original.terminal_ids)
    owned = replace(original, variables=variables, site_family_ids=sites, terminal_ids=terminals)
    original_payload = original.as_dict()
    variables.reverse()
    sites.append("SITE-UNDECLARED")
    terminals.clear()
    assert owned.as_dict() == original_payload
    assert owned.index_of("N_E") == owned.state_ids.index("N_E")
    network = build_reaction_network(owned)
    assert audit_reaction_network(network, owned).decision == GateDecision.PASS
    assert network.as_dict() == build_reaction_network(original).as_dict()


@pytest.mark.parametrize("reorder", [False, True])
def test_no_reaction_feed_preserves_species_identity_against_analytic_balance(reorder):
    state = _state()
    if reorder:
        variables = list(state.variables)
        variables[0], variables[1] = variables[1], variables[0]
        state = replace(
            state,
            variables=tuple(replace(variable, index=i) for i, variable in enumerate(variables)),
        )
    network = build_reaction_network(state)
    assert audit_reaction_network(network, state).decision == GateDecision.PASS
    assert network.state_ids == state.state_ids
    package = build_calculated_reference_rate_package(network)
    package = replace(
        package, bindings=tuple(replace(binding, enabled=False) for binding in package.bindings)
    )
    feed = list(state.zeros())
    feed[state.index_of("N_E")] = 0.2
    initial = state.pack({"N_E": 0.3, "N_P": 0.4, "N_SOLVENT": 3.0}, fill_missing=0.0)
    rhs = execute_structural_rhs(
        network,
        state,
        package,
        initial,
        temperature_k=323.15,
        volume_m3=1.0,
        feed_mol_s=feed,
    )
    assert rhs.decision == GateDecision.PASS
    assert rhs.rhs[state.index_of("N_E")] == pytest.approx(0.2)
    assert rhs.rhs[state.index_of("N_P")] == 0.0
    request = build_integration_request(
        network,
        state,
        package,
        time_start_s=0.0,
        time_end_s=1.0,
        initial_step_s=0.1,
        minimum_step_s=1e-8,
        maximum_step_s=0.25,
        relative_tolerance=1e-8,
        absolute_tolerance=1e-11,
        maximum_steps=10000,
    )
    result = integrate_adaptive(
        request,
        network,
        state,
        package,
        initial,
        temperature_k=323.15,
        volume_m3=1.0,
        feed_mol_s=feed,
    )
    assert result.decision == GateDecision.PASS
    final = state.unpack(result.final_state)
    # With every reaction disabled, dN_i/dt = F_i. These independent species
    # balances detect relabelled feed even when total inventory still closes.
    assert final["N_E"] == pytest.approx(0.3 + 0.2 * 1.0, abs=1e-12)
    assert final["N_P"] == pytest.approx(0.4, abs=1e-12)
    assert final["N_SOLVENT"] == pytest.approx(3.0, abs=1e-12)
    assert sum(result.final_state) - sum(initial) == pytest.approx(0.2, abs=1e-12)
    assert result.conservation["external_feed_integral_mol"] == pytest.approx(0.2)
    assert result.scientific_technical_approval == "NOT_EVALUATED"


def _refresh_digest(record):
    payload = {key: value for key, value in record.items() if key != "digest_sha256"}
    record["digest_sha256"] = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _reordered_project(*, correct_indices):
    path = Path(__file__).resolve().parents[1] / "fixtures/v2_phase_a2_reference_project.json"
    project = json.loads(path.read_text(encoding="utf-8"))
    state = project["generated_state_definitions"][0]
    variables = state["variables"]
    variables[0], variables[1] = variables[1], variables[0]
    if correct_indices:
        for i, variable in enumerate(variables):
            variable["index"] = i
    _refresh_digest(state)
    network = project["reaction_networks"][0]
    network["state_ids"][0], network["state_ids"][1] = (
        network["state_ids"][1],
        network["state_ids"][0],
    )
    matrix = network["stoichiometric_matrix"]
    matrix[0], matrix[1] = matrix[1], matrix[0]
    network["generated_state_digest_sha256"] = state["digest_sha256"]
    _refresh_digest(network)
    return project


def test_serialized_state_layout_cannot_be_laundered_by_matching_network_and_digests():
    project = _reordered_project(correct_indices=False)
    result = validate_v2_project(project)
    assert result.decision == GateDecision.FAIL
    assert any(
        "indices" in issue.message and "position" in issue.message for issue in result.errors
    )
    with pytest.raises(CanonicalProjectLoadError, match="indices.*position"):
        load_canonical_project(project)


def test_consistently_reordered_state_and_network_can_be_published():
    project = _reordered_project(correct_indices=True)
    assert validate_v2_project(project).decision == GateDecision.PASS
    published = load_canonical_project(project)
    assert (
        published.canonical_project["generated_state_definitions"][0]["variables"][0]["state_id"]
        == "N_P"
    )
