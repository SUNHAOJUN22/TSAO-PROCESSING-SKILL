"""Synthetic work packages must cover the declared gate/workstream matrix once."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tsao.gates import gate_event_digest
from tsao.project import audit_project, bootstrap_project

MODES = ("initialization", "project", "transition", "release")
MISSING = object()


def make_project(tmp_path: Path, mode: str) -> tuple[Path, Path, list[dict]]:
    brief = tmp_path / "brief.yaml"
    brief.write_text("project_id: SYNTHETIC-MATRIX\ntitle: Generic process\n", encoding="utf-8")
    root = tmp_path / "project"
    bootstrap_project(brief, root)
    if mode == "release":
        manifest_path = root / "project_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        events = []
        previous = None
        for gate in manifest["gates"]:
            gate.update(
                status="PASS",
                owner="synthetic owner",
                evidence_ids=["synthetic-evidence"],
                approval_status="APPROVED",
                approver="synthetic reviewer",
            )
            event = {
                "event_id": "synthetic-" + gate["gate_id"],
                "gate_id": gate["gate_id"],
                "old_status": "NOT_EVALUATED",
                "new_status": "PASS",
                "actor": "synthetic owner",
                "approver": "synthetic reviewer",
                "evidence_ids": ["synthetic-evidence"],
                "reason": "software test fixture",
                "timestamp": "2026-11-22T03:00:00Z",
                "previous_event_digest": previous,
            }
            event["event_digest"] = gate_event_digest(event)
            previous = event["event_digest"]
            events.append(event)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        (root / "00_governance/gate_events.jsonl").write_text(
            "".join(json.dumps(event) + "\n" for event in events), encoding="utf-8"
        )
    assert audit_project(root, mode=mode) == []
    path = root / "00_governance/work_packages.json"
    return root, path, json.loads(path.read_text(encoding="utf-8"))


def damage(packages: list[dict], case: str) -> None:
    if case == "all-duplicate":
        packages[:] = [copy.deepcopy(packages[0]) for _ in packages]
    elif case == "one-duplicate":
        packages[-1] = copy.deepcopy(packages[0])
    elif case == "duplicate-coordinate-new-id":
        packages[-1] = dict(packages[0], work_package_id="synthetic-other")
    elif case == "duplicate-id":
        packages[-1]["work_package_id"] = packages[0]["work_package_id"]
    elif case == "unknown-gate":
        packages[-1]["gate_id"] = "G19"
    elif case == "unknown-workstream":
        packages[-1]["workstream_id"] = "unknown-stream"
    else:
        raise AssertionError(case)


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize(
    "case",
    [
        "all-duplicate",
        "one-duplicate",
        "duplicate-coordinate-new-id",
        "duplicate-id",
        "unknown-gate",
        "unknown-workstream",
    ],
)
def test_full_record_count_cannot_hide_missing_or_repeated_identity(
    tmp_path: Path, mode: str, case: str
) -> None:
    root, path, packages = make_project(tmp_path, mode)
    damage(packages, case)
    path.write_text(json.dumps(packages), encoding="utf-8")
    assert len(packages) == 266
    issues = audit_project(root, mode=mode)
    assert any("work package" in issue for issue in issues), issues


@pytest.mark.parametrize("field", ["work_package_id", "gate_id", "workstream_id"])
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(MISSING, id="missing"),
        pytest.param(None, id="null"),
        pytest.param(" ", id="blank"),
        pytest.param([], id="array"),
        pytest.param(True, id="boolean"),
    ],
)
def test_matrix_identity_fields_require_explicit_text(
    tmp_path: Path, field: str, value: object
) -> None:
    root, path, packages = make_project(tmp_path, "initialization")
    if value is MISSING:
        packages[-1].pop(field)
    else:
        packages[-1][field] = value
    path.write_text(json.dumps(packages), encoding="utf-8")
    issues = audit_project(root)
    assert any("work package" in issue for issue in issues), issues


@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("change", ["reorder", "custom-ids"])
def test_complete_matrix_preserves_order_and_custom_identity_compatibility(
    tmp_path: Path, mode: str, change: str
) -> None:
    root, path, packages = make_project(tmp_path, mode)
    if change == "reorder":
        packages.reverse()
    else:
        for index, package in enumerate(packages):
            package["work_package_id"] = f"custom-work-package-{index}"
    path.write_text(json.dumps(packages), encoding="utf-8")
    assert audit_project(root, mode=mode) == []


@pytest.mark.parametrize("mode", MODES)
def test_public_audit_cli_rejects_duplicate_matrix_without_rewriting_it(
    tmp_path: Path, mode: str
) -> None:
    root, path, packages = make_project(tmp_path, mode)
    damage(packages, "duplicate-coordinate-new-id")
    path.write_text(json.dumps(packages), encoding="utf-8")
    before = path.read_bytes()
    result = subprocess.run(
        [sys.executable, "-m", "tsao.cli", "audit", mode, "--root", str(root)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["pass"] is False and report["mode"] == mode
    assert any("work package" in issue for issue in report["issues"])
    assert path.read_bytes() == before
