"""Project gate snapshots must match their recorded terminal states."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tsao.gates import gate_event_digest, validate_gate_events
from tsao.project import audit_project, bootstrap_project


@pytest.fixture
def project(tmp_path: Path) -> Path:
    brief = tmp_path / "brief.yaml"
    brief.write_text("project_id: SYNTHETIC-LEDGER\ntitle: Generic process\n", encoding="utf-8")
    root = tmp_path / "project"
    bootstrap_project(brief, root)
    return root


def set_manifest_statuses(root: Path, statuses: dict[str, str]) -> None:
    path = root / "project_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for gate in manifest["gates"]:
        if gate["gate_id"] in statuses:
            gate.update(
                status=statuses[gate["gate_id"]],
                owner="synthetic owner",
                evidence_ids=["E-" + gate["gate_id"]],
                approval_status="APPROVED",
                approver="synthetic reviewer",
            )
    path.write_text(json.dumps(manifest), encoding="utf-8")


def write_events(root: Path, transitions: list[tuple[str, str]]) -> list[dict]:
    events: list[dict] = []
    states: dict[str, str] = {}
    previous = None
    for index, (gate_id, status) in enumerate(transitions):
        event = {
            "event_id": f"event-{index}",
            "gate_id": gate_id,
            "old_status": states.get(gate_id, "NOT_EVALUATED"),
            "new_status": status,
            "actor": "synthetic owner",
            "approver": "synthetic reviewer",
            "evidence_ids": ["E-" + gate_id],
            "reason": "synthetic software contract fixture",
            "timestamp": "2026-11-21T09:00:00Z",
            "previous_event_digest": previous,
        }
        event["event_digest"] = gate_event_digest(event)
        previous = event["event_digest"]
        states[gate_id] = status
        events.append(event)
    assert validate_gate_events(events) == []
    (root / "00_governance/gate_events.jsonl").write_text(
        "".join(json.dumps(event) + "\n" for event in events), encoding="utf-8"
    )
    return events


def complete_pass_history() -> list[tuple[str, str]]:
    return [(f"G{index}", "PASS") for index in range(19)]


@pytest.mark.parametrize("mode", ["transition", "release"])
def test_pass_manifest_cannot_bypass_an_incomplete_hold_ledger(project: Path, mode: str) -> None:
    set_manifest_statuses(project, dict(complete_pass_history()))
    write_events(project, [("G0", "HOLD")])
    issues = audit_project(project, mode=mode)
    assert any("G0" in issue and "HOLD" in issue and "ledger" in issue for issue in issues)
    assert any("G1" in issue and "NOT_EVALUATED" in issue for issue in issues)


@pytest.mark.parametrize("mode", ["transition", "release"])
def test_latest_rollback_event_cannot_be_hidden_by_an_older_pass(project: Path, mode: str) -> None:
    set_manifest_statuses(project, dict(complete_pass_history()))
    write_events(project, complete_pass_history() + [("G18", "HOLD")])
    issues = audit_project(project, mode=mode)
    assert any("G18" in issue and "HOLD" in issue and "ledger" in issue for issue in issues)


@pytest.mark.parametrize("mode", ["transition", "release"])
def test_gate_without_any_event_is_not_evaluated(project: Path, mode: str) -> None:
    set_manifest_statuses(project, dict(complete_pass_history()))
    write_events(project, complete_pass_history()[:-1])
    issues = audit_project(project, mode=mode)
    assert any("G18" in issue and "NOT_EVALUATED" in issue for issue in issues)


def test_history_cannot_advance_a_stale_manifest_silently(project: Path) -> None:
    write_events(project, [("G0", "HOLD")])
    issues = audit_project(project, mode="transition")
    assert any("G0" in issue and "HOLD" in issue and "ledger" in issue for issue in issues)


def test_release_cli_rejects_mismatch_without_changing_source_records(project: Path) -> None:
    set_manifest_statuses(project, dict(complete_pass_history()))
    write_events(project, [("G0", "HOLD")])
    paths = [project / "project_manifest.json", project / "00_governance/gate_events.jsonl"]
    before = [path.read_bytes() for path in paths]
    process = subprocess.run(
        [sys.executable, "-m", "tsao.cli", "audit", "release", "--root", str(project)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert process.returncode == 2, process.stdout + process.stderr
    report = json.loads(process.stdout)
    assert report["pass"] is False and report["mode"] == "release"
    assert any("ledger" in issue for issue in report["issues"])
    assert [path.read_bytes() for path in paths] == before


@pytest.mark.parametrize("terminal", ["PASS", "RETIRED"])
def test_matching_complete_release_history_remains_valid(project: Path, terminal: str) -> None:
    transitions = complete_pass_history() + [("G18", "HOLD"), ("G18", terminal)]
    statuses = dict(transitions)
    set_manifest_statuses(project, statuses)
    write_events(project, transitions)
    assert audit_project(project, mode="release") == []


def test_transition_accepts_a_matching_partial_history(project: Path) -> None:
    set_manifest_statuses(project, {"G0": "HOLD"})
    write_events(project, [("G0", "HOLD")])
    assert audit_project(project, mode="transition") == []


def test_transition_accepts_an_unstarted_project(project: Path) -> None:
    assert audit_project(project, mode="transition") == []


def test_invalid_event_chain_keeps_its_validation_diagnostic(project: Path) -> None:
    events = write_events(project, [("G0", "HOLD")])
    events[0]["new_status"] = "INVALID"
    (project / "00_governance/gate_events.jsonl").write_text(
        json.dumps(events[0]) + "\n", encoding="utf-8"
    )
    issues = audit_project(project, mode="transition")
    assert any("invalid status" in issue for issue in issues)


def test_project_mode_preserves_its_snapshot_only_contract(project: Path) -> None:
    set_manifest_statuses(project, dict(complete_pass_history()))
    assert audit_project(project, mode="project") == []
