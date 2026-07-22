from __future__ import annotations

import json
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from ._utils import atomic_write_text, nonempty, required_or_default_string
from .gates import ApprovalStatus, GateRecord, GateStatus, validate_gate_sequence
from .routing import route

PROJECT_DIRS = (
    "00_governance",
    "01_evidence",
    "02_requirements",
    "03_measurement_data",
    "04_chemistry",
    "05_models",
    "06_lab",
    "07_bench",
    "08_separation_recycle",
    "09_pilot",
    "10_demonstration",
    "11_industrial",
    "12_control",
    "13_hse_reliability",
    "14_tea_lca_ip",
    "15_qualification",
    "16_technology_package",
    "17_transfer",
    "18_field_learning",
    "data/raw",
    "data/processed",
    "models",
    "reports",
    "logs",
)
_VALID_SUBSKILLS = {"epdm", "poe", "polymer-general"}


def bootstrap_project(
    brief: Path, output: Path, template_root: Path | None = None
) -> dict[str, Any]:
    brief = Path(brief)
    output = Path(output)
    if not brief.is_file():
        raise FileNotFoundError(f"brief file not found: {brief}")
    if output.exists():
        if not output.is_dir():
            raise FileExistsError("output path exists and is not a directory")
        if any(output.iterdir()):
            raise FileExistsError("output directory is not empty")
    text = brief.read_text(encoding="utf-8")
    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML brief: {exc}") from exc
    data: Mapping[str, Any]
    if loaded is None:
        data = {}
    elif isinstance(loaded, Mapping):
        data = loaded
    else:
        raise ValueError("brief root must be a YAML mapping")
    project_id = required_or_default_string(data, "project_id", "TSAO-PROJECT")
    title = required_or_default_string(data, "title", "Untitled process project")
    if template_root is not None:
        template_root = Path(template_root)
        if template_root.exists() and not template_root.is_dir():
            raise ValueError("template root must be a directory")
        if template_root.is_symlink():
            raise ValueError("template root must not be a symlink")
        if template_root.exists():
            for path in template_root.rglob("*"):
                if path.is_symlink():
                    raise ValueError(f"template tree contains symlink: {path}")
    output.mkdir(parents=True, exist_ok=True)
    for directory in PROJECT_DIRS:
        (output / directory).mkdir(parents=True, exist_ok=True)
    if template_root and template_root.exists():
        for path in sorted(template_root.rglob("*")):
            if path.is_file():
                relative = path.relative_to(template_root)
                destination = output / "00_governance" / "templates" / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
    routed = route(text)
    manifest: dict[str, Any] = {
        "project_id": project_id,
        "title": title,
        "version": "0.1.0-alpha.2",
        "domain": [item[0] for item in routed],
        "subskills": [item[0] for item in routed if item[0] in _VALID_SUBSKILLS],
        "technical_approval_status": "NOT_EVALUATED",
        "gates": [
            {
                "gate_id": f"G{index}",
                "status": "NOT_EVALUATED",
                "owner": None,
                "evidence_ids": [],
                "approval_status": "NOT_EVALUATED",
                "approver": None,
            }
            for index in range(19)
        ],
    }
    atomic_write_text(
        output / "project_manifest.json",
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    )
    atomic_write_text(output / "brief.yaml", text)
    return manifest


def audit_project(root: Path) -> list[str]:
    root = Path(root)
    if not root.exists():
        return ["project root does not exist"]
    if not root.is_dir():
        return ["project root is not a directory"]
    issues: list[str] = []
    if root.is_symlink():
        issues.append("project root must not be a symlink")
    for path in root.rglob("*"):
        if path.is_symlink():
            issues.append(f"project contains symlink: {path.relative_to(root).as_posix()}")
    issues.extend(
        f"missing directory: {directory}"
        for directory in PROJECT_DIRS
        if not (root / directory).is_dir()
    )
    manifest_path = root / "project_manifest.json"
    if not manifest_path.is_file():
        return sorted(set(issues + ["missing project_manifest.json"]))
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return sorted(set(issues + [f"invalid project manifest: {exc}"]))
    if not isinstance(data, dict):
        return sorted(set(issues + ["project manifest must be an object"]))
    for key in ("project_id", "title", "version"):
        if not nonempty(data.get(key)):
            issues.append(f"manifest field must be a non-empty string: {key}")
    domain = data.get("domain")
    if not isinstance(domain, list) or not domain or any(not nonempty(item) for item in domain):
        issues.append("domain must be a non-empty string array")
    subskills = data.get("subskills")
    if (
        not isinstance(subskills, list)
        or len(subskills) != len(set(subskills))
        or any(item not in _VALID_SUBSKILLS for item in subskills)
    ):
        issues.append("subskills must be unique supported subskill names")
    if data.get("technical_approval_status") != "NOT_EVALUATED":
        issues.append("project must not claim technical approval")
    raw_gates = data.get("gates")
    gate_records: list[GateRecord] = []
    if not isinstance(raw_gates, list):
        issues.append("gates must be an array")
    else:
        for index, raw_gate in enumerate(raw_gates):
            if not isinstance(raw_gate, dict):
                issues.append(f"gate at index {index} must be an object")
                continue
            try:
                gate_records.append(
                    GateRecord(
                        gate_id=raw_gate["gate_id"],
                        status=GateStatus(raw_gate["status"]),
                        owner=raw_gate.get("owner"),
                        evidence_ids=list(raw_gate.get("evidence_ids", [])),
                        approval_status=ApprovalStatus(raw_gate["approval_status"]),
                        approver=raw_gate.get("approver"),
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                issues.append(f"invalid gate at index {index}: {exc}")
        if len(gate_records) == len(raw_gates):
            issues.extend(validate_gate_sequence(gate_records))
        if [gate.gate_id for gate in gate_records] != [f"G{i}" for i in range(19)]:
            issues.append("gate sequence must be ordered G0-G18")
    return sorted(set(issues))
