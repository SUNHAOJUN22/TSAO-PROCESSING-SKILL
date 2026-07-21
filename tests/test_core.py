from datetime import date
from pathlib import Path
import json

import pytest

from tsao.core import (
    ApprovalStatus,
    AssuranceGraph,
    EvidenceItem,
    GateRecord,
    GateStatus,
    ModelRecord,
    audit_project,
    balance_residual,
    bootstrap_project,
    closure_fraction,
    deterministic_zip,
    route,
    stoichiometric_rank,
    validate_gate_sequence,
)


def test_router_selects_epdm_and_master_polymer():
    selected = dict(route("metallocene EPDM with ENB solution polymerization"))
    assert selected["epdm"] > 0
    assert selected["polymer-general"] > 0


def test_router_selects_poe():
    assert route("POE ethylene octene solution polymerization")[0][0] == "poe"


def test_gate_pass_is_fail_closed():
    gate = GateRecord("G3", status=GateStatus.PASS)
    assert set(gate.validate()) == {
        "PASS requires owner",
        "PASS requires evidence",
        "PASS requires approval",
        "PASS requires named approver",
    }


def test_gate_pass_with_evidence_and_approval():
    gate = GateRecord(
        "G0",
        status=GateStatus.PASS,
        owner="project manager",
        evidence_ids=["EV-001"],
        approval_status=ApprovalStatus.APPROVED,
        approver="steering committee chair",
    )
    assert gate.validate() == []


def test_illegal_gate_transition_rejected():
    gate = GateRecord("G0", status=GateStatus.RETIRED)
    with pytest.raises(ValueError):
        gate.transition(GateStatus.PASS)


def test_gate_sequence_blocks_skipping():
    gates = [GateRecord(f"G{i}") for i in range(19)]
    gates[1] = GateRecord(
        "G1",
        status=GateStatus.PASS,
        owner="owner",
        evidence_ids=["EV-1"],
        approval_status=ApprovalStatus.APPROVED,
        approver="approver",
    )
    assert "G1 cannot PASS before G0" in validate_gate_sequence(gates)


def test_evidence_rejects_expired_or_open_contradiction():
    expired = EvidenceItem("EV-1", "A", True, "matching chemistry", "2020-01-01")
    contradicted = EvidenceItem("EV-2", "A", True, "matching chemistry", "2030-01-01", "OPEN")
    assert not expired.usable(date(2026, 7, 21))
    assert not contradicted.usable(date(2026, 7, 21))


def test_high_risk_model_requires_independent_review():
    model = ModelRecord("M-1", "MR5", "QUALIFIED", "PASS")
    assert not model.qualified()
    model.independent_reviewer = "independent reviewer"
    assert model.qualified()


def test_mass_balance_and_closure():
    assert balance_residual({"A": 10}, {"A": 9.8})["A"] == pytest.approx(0.2)
    assert closure_fraction({"A": 10}, {"A": 9.8}) == pytest.approx(0.98)


def test_stoichiometric_rank():
    assert stoichiometric_rank([[1, -1, 0], [0, 1, -1]]) == 2


def test_assurance_graph_path_and_orphans():
    graph = AssuranceGraph()
    graph.add_node("R1", "requirement")
    graph.add_node("E1", "evidence")
    graph.add_node("G1", "gate")
    graph.add_edge("R1", "E1", "supported_by")
    graph.add_edge("E1", "G1", "supports")
    assert graph.has_path("R1", "G1")
    assert graph.orphans() == []


def test_project_bootstrap_and_audit(tmp_path: Path):
    brief = tmp_path / "brief.yaml"
    brief.write_text("project_id: DEMO\ntitle: EPDM pilot\nsummary: metallocene EPDM ENB\n", encoding="utf-8")
    root = tmp_path / "project"
    manifest = bootstrap_project(brief, root)
    assert "epdm" in manifest["subskills"]
    assert manifest["technical_approval_status"] == "NOT_EVALUATED"
    assert audit_project(root) == []


def test_project_audit_rejects_false_approval(tmp_path: Path):
    brief = tmp_path / "brief.yaml"
    brief.write_text("project_id: DEMO\ntitle: Generic process\n", encoding="utf-8")
    root = tmp_path / "project"
    bootstrap_project(brief, root)
    manifest_path = root / "project_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["technical_approval_status"] = "APPROVED"
    manifest_path.write_text(json.dumps(manifest))
    assert "project must not claim technical approval" in audit_project(root)


def test_deterministic_archive(tmp_path: Path):
    root = tmp_path / "source"
    root.mkdir()
    (root / "a.txt").write_text("alpha")
    first = tmp_path / "one.zip"
    second = tmp_path / "two.zip"
    assert deterministic_zip(root, first) == deterministic_zip(root, second)
    assert first.read_bytes() == second.read_bytes()
