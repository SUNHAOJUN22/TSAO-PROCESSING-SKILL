from __future__ import annotations

import hashlib
import json
import math
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
from skills.epdm.reaction_network import build_reaction_network
from skills.epdm.state_generator import generate_state_definition
from skills.epdm.validation_v2 import validate_v2_project


def _system():
    state = generate_state_definition(
        source_state_definition_id="STATE-MATRIX-IDENTITY",
        model_level=2,
        site_family_ids=("SITE-A",),
    )
    return state, build_reaction_network(state)


@pytest.mark.parametrize("coefficients", [(-2.0, 2.0), (0.0, 1.0), (-1.0, 0.0)])
def test_typed_network_rejects_matrix_declaration_divergence(coefficients):
    state, network = _system()
    matrix = [list(row) for row in network.stoichiometric_matrix]
    column = network._channel_index["ACT_SPON:SITE-A"]
    matrix[state.index_of("N_SITE_POTENTIAL:SITE-A")][column] = coefficients[0]
    matrix[state.index_of("N_SITE_VACANT:SITE-A")][column] = coefficients[1]
    with pytest.raises(ContractValidationError, match="stoichiometr"):
        replace(network, stoichiometric_matrix=matrix)


def test_matrix_cannot_add_an_undeclared_species():
    state, network = _system()
    matrix = [list(row) for row in network.stoichiometric_matrix]
    matrix[state.index_of("N_SOLVENT")][0] = 1.0
    with pytest.raises(ContractValidationError, match="stoichiometr"):
        replace(network, stoichiometric_matrix=matrix)


def test_network_owns_mutable_inputs_before_validation_and_caching():
    _, network = _system()
    matrix = [list(row) for row in network.stoichiometric_matrix]
    channels = list(network.channels)
    terms = list(channels[0].stoichiometry)
    reactants = list(channels[0].reactant_state_ids)
    channels[0] = replace(channels[0], stoichiometry=terms, reactant_state_ids=reactants)
    state_ids = list(network.state_ids)
    owned = replace(network, channels=channels, state_ids=state_ids, stoichiometric_matrix=matrix)
    digest = owned.digest_sha256
    matrix[0][0] = 12.0
    channels.clear()
    terms.clear()
    reactants.clear()
    state_ids.reverse()
    assert owned.digest_sha256 == digest
    assert owned.as_dict() == network.as_dict()


@pytest.mark.parametrize("refresh_digest", [False, True])
def test_serialized_matrix_cannot_be_laundered_by_a_fresh_digest(refresh_digest):
    fixture = Path(__file__).resolve().parents[1] / "fixtures/v2_phase_a2_reference_project.json"
    project = json.loads(fixture.read_text(encoding="utf-8"))
    network = project["reaction_networks"][0]
    column = next(i for i, c in enumerate(network["channels"]) if c["family"] == "ACT_SPON")
    for row in network["stoichiometric_matrix"]:
        row[column] *= 2.0
    if refresh_digest:
        payload = {key: value for key, value in network.items() if key != "digest_sha256"}
        network["digest_sha256"] = hashlib.sha256(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
    assert validate_v2_project(project).decision == GateDecision.FAIL
    with pytest.raises(CanonicalProjectLoadError, match="stoichiometr"):
        load_canonical_project(project)


def test_activation_pipeline_matches_independent_closed_form():
    state, network = _system()
    package = build_calculated_reference_rate_package(network)
    package = replace(
        package,
        bindings=tuple(
            replace(binding, enabled=binding.reaction_id == "ACT_SPON:SITE-A")
            for binding in package.bindings
        ),
    )
    vector = state.pack({"N_SITE_POTENTIAL:SITE-A": 2.0}, fill_missing=0.0)
    rhs = execute_structural_rhs(
        network, state, package, vector, temperature_k=323.15, volume_m3=1.0
    )
    potential = state.index_of("N_SITE_POTENTIAL:SITE-A")
    vacant = state.index_of("N_SITE_VACANT:SITE-A")
    assert rhs.decision == GateDecision.PASS
    assert rhs.rhs[potential] == pytest.approx(-0.004)
    assert rhs.rhs[vacant] == pytest.approx(0.004)
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
        request, network, state, package, vector, temperature_k=323.15, volume_m3=1.0
    )
    assert result.decision == GateDecision.PASS
    assert result.final_state[potential] == pytest.approx(2.0 * math.exp(-0.002), abs=1e-12)
    assert result.final_state[potential] + result.final_state[vacant] == pytest.approx(2.0)
    assert result.as_dict()["scientific_technical_approval"] == "NOT_EVALUATED"
