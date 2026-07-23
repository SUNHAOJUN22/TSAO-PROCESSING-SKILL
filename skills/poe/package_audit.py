from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator

from .governance import blocking_conflicts
from .qualification import qualify_property_method, validate_process_case

_PLACEHOLDER_PATTERNS = (
    "qualified placeholder",
    "placeholder",
    "tbd",
    "todo",
    "待补充",
    "占位",
    "lorem ipsum",
)
_REQUIRED_PACKAGE_GROUPS = {
    "design_basis": ("design_basis", "设计基础", "工艺设计基础"),
    "pfd": ("pfd", "工艺流程图", "流程图"),
    "material_energy_balance": (
        "material_energy_balance",
        "物料衡算",
        "能量衡算",
        "物料和能量衡算",
    ),
    "equipment": ("equipment", "设备表", "设备数据"),
    "instrument_control": ("instrument_control", "仪表控制", "控制方案", "控制说明"),
    "utilities": ("utilities", "公用工程", "公用工程数据"),
    "model_validation": ("model_validation", "模型验证", "模拟报告", "模型报告"),
    "acceptance": ("acceptance", "验收", "验收矩阵", "验收报告"),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _safe_relative(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        return False
    pure = PurePosixPath(value)
    return not pure.is_absolute() and ".." not in pure.parts and not pure.parts[0].endswith(":")


def _looks_like_placeholder(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8").strip().casefold()
    except (UnicodeError, OSError):
        return False
    if len(text) < 64:
        return True
    return any(pattern in text for pattern in _PLACEHOLDER_PATTERNS)


def _legacy_discovery(root: Path) -> dict[str, list[str]]:
    found = {key: [] for key in _REQUIRED_PACKAGE_GROUPS}
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        normalized = path.relative_to(root).as_posix().casefold().replace("-", "_")
        for group, aliases in _REQUIRED_PACKAGE_GROUPS.items():
            if any(alias.casefold().replace("-", "_") in normalized for alias in aliases):
                found[group].append(path.relative_to(root).as_posix())
    return found


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(data, dict):
        return None, "JSON root must be an object"
    return data, None


def _validate_package_requirement_trace(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    holds: list[str] = []
    requirements = data.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        holds.append("package requirement trace is empty")
        return errors, holds
    seen: set[str] = set()
    for index, item in enumerate(requirements, start=1):
        if not isinstance(item, dict):
            errors.append(f"requirement trace row {index} must be an object")
            continue
        requirement_id = item.get("requirement_id")
        if (
            not isinstance(requirement_id, str)
            or not requirement_id.strip()
            or requirement_id in seen
        ):
            errors.append(f"requirement trace row {index} has invalid or duplicate requirement_id")
        else:
            seen.add(requirement_id)
        if not item.get("criterion") or not item.get("verification_method"):
            holds.append(
                f"requirement {requirement_id or index} lacks criterion or verification method"
            )
        if item.get("status") == "PASS" and not item.get("approver"):
            errors.append(f"requirement {requirement_id or index}: PASS requires named approver")
        evidence_ids = item.get("evidence_ids")
        if not isinstance(evidence_ids, list) or not evidence_ids:
            holds.append(f"requirement {requirement_id or index} has no evidence_ids")
    return errors, holds


def _validate_package_conflicts(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    holds: list[str] = []
    conflicts = data.get("conflicts")
    if not isinstance(conflicts, list):
        errors.append("conflict ledger conflicts must be a list")
        return errors, holds
    seen: set[str] = set()
    for index, item in enumerate(conflicts, start=1):
        if not isinstance(item, dict):
            errors.append(f"conflict row {index} must be an object")
            continue
        conflict_id = item.get("conflict_id")
        if not isinstance(conflict_id, str) or not conflict_id.strip() or conflict_id in seen:
            errors.append(f"conflict row {index} has invalid or duplicate conflict_id")
        else:
            seen.add(conflict_id)
        status = item.get("status")
        if status not in {"OPEN", "MITIGATED", "RESOLVED", "REJECTED"}:
            errors.append(f"conflict {conflict_id or index} has invalid status")
        if status == "OPEN":
            holds.append(f"conflict {conflict_id or index} remains OPEN")
        elif status in {"MITIGATED", "RESOLVED", "REJECTED"} and not item.get("approver"):
            errors.append(f"conflict {conflict_id or index}: {status} requires named approver")
    return errors, holds


def audit_process_package(root: Path) -> dict[str, Any]:
    root = Path(root)
    errors: list[str] = []
    holds: list[str] = []
    if not root.is_dir() or root.is_symlink():
        return {
            "root": str(root),
            "status": "FAIL",
            "pass": False,
            "errors": ["package root must be a real directory"],
            "holds": [],
        }
    for path in root.rglob("*"):
        if path.is_symlink():
            errors.append(f"package contains symlink: {path.relative_to(root).as_posix()}")
        elif path.is_file() and path.stat().st_size == 0:
            errors.append(f"empty file: {path.relative_to(root).as_posix()}")
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        discovered = _legacy_discovery(root)
        missing = [group for group, values in discovered.items() if not values]
        if missing:
            holds.append(
                "legacy package is unmanifested and missing mapped groups: " + ", ".join(missing)
            )
        else:
            holds.append(
                "rich legacy package discovered, but manifest/content cross-references are required"
            )
        return {
            "root": str(root),
            "status": "FAIL" if errors else "HOLD",
            "pass": False,
            "errors": sorted(set(errors)),
            "holds": sorted(set(holds)),
            "legacy_discovery": discovered,
        }
    manifest, manifest_error = _load_json(manifest_path)
    if manifest_error or manifest is None:
        return {
            "root": str(root),
            "status": "FAIL",
            "pass": False,
            "errors": [f"invalid manifest: {manifest_error}"],
            "holds": [],
        }
    schema_path = Path(__file__).parent / "schemas/package_manifest.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema_errors = sorted(
            error.message for error in Draft202012Validator(schema).iter_errors(manifest)
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        schema_errors = [f"cannot load package manifest schema: {exc}"]
    errors.extend(f"manifest schema: {item}" for item in schema_errors)
    files = manifest.get("files")
    if not isinstance(files, list):
        errors.append("manifest.files must be a list")
        files = []
    groups: set[str] = set()
    deliverable_ids: set[str] = set()
    paths: set[str] = set()
    for index, record in enumerate(files, start=1):
        if not isinstance(record, dict):
            errors.append(f"manifest file record {index} must be an object")
            continue
        deliverable_id = record.get("deliverable_id")
        if (
            not isinstance(deliverable_id, str)
            or not deliverable_id.strip()
            or deliverable_id in deliverable_ids
        ):
            errors.append(f"invalid or duplicate deliverable_id: {deliverable_id}")
        else:
            deliverable_ids.add(deliverable_id)
        group = record.get("group")
        if group not in _REQUIRED_PACKAGE_GROUPS:
            errors.append(f"unknown deliverable group: {group}")
        else:
            groups.add(group)
        rel = record.get("path")
        if not _safe_relative(rel):
            errors.append(f"unsafe manifest path: {rel}")
            continue
        if rel in paths:
            errors.append(f"duplicate manifest path: {rel}")
        paths.add(rel)
        path = root / rel
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing or unsafe manifest file: {rel}")
            continue
        size = record.get("bytes")
        if isinstance(size, bool) or not isinstance(size, int) or size != path.stat().st_size:
            errors.append(f"byte-count mismatch: {rel}")
        if record.get("sha256") != _sha256(path):
            errors.append(f"SHA-256 mismatch: {rel}")
        if _looks_like_placeholder(path):
            errors.append(f"placeholder or content-free deliverable: {rel}")
        evidence_ids = record.get("evidence_ids")
        if (
            not isinstance(evidence_ids, list)
            or not evidence_ids
            or any(not isinstance(item, str) or not item.strip() for item in evidence_ids)
        ):
            holds.append(f"deliverable has no valid evidence_ids: {rel}")
    missing_groups = sorted(set(_REQUIRED_PACKAGE_GROUPS) - groups)
    if missing_groups:
        errors.append("missing deliverable groups: " + ", ".join(missing_groups))
    structured_records = manifest.get("structured_records")
    if not isinstance(structured_records, dict):
        errors.append("structured_records must be an object")
        structured_records = {}
    loaded_records: dict[str, dict[str, Any]] = {}
    for name in (
        "property_method",
        "process_case",
        "acceptance",
        "requirement_trace",
        "conflict_ledger",
    ):
        rel = structured_records.get(name)
        if not rel:
            holds.append(f"missing structured record: {name}")
            continue
        if not _safe_relative(rel):
            errors.append(f"unsafe structured record path: {rel}")
            continue
        path = root / rel
        if not path.is_file() or path.is_symlink():
            errors.append(f"missing or unsafe structured record file: {rel}")
            continue
        data, load_error = _load_json(path)
        if load_error or data is None:
            errors.append(f"invalid structured record {rel}: {load_error}")
            continue
        loaded_records[name] = data
        if name == "property_method":
            result = qualify_property_method(data)
            if result["status"] == "FAIL":
                errors.extend(f"{rel}: {item}" for item in result["errors"])
            elif result["status"] == "HOLD":
                holds.extend(f"{rel}: {item}" for item in result["holds"])
        elif name == "process_case":
            result = validate_process_case(data)
            if result["status"] == "FAIL":
                errors.extend(f"{rel}: {item}" for item in result["errors"])
            elif result["status"] == "HOLD":
                holds.extend(f"{rel}: {item}" for item in result["holds"])
        elif name == "requirement_trace":
            trace_errors, trace_holds = _validate_package_requirement_trace(data)
            errors.extend(f"{rel}: {item}" for item in trace_errors)
            holds.extend(f"{rel}: {item}" for item in trace_holds)
        elif name == "conflict_ledger":
            conflict_errors, conflict_holds = _validate_package_conflicts(data)
            errors.extend(f"{rel}: {item}" for item in conflict_errors)
            holds.extend(f"{rel}: {item}" for item in conflict_holds)
            if blocking_conflicts(data):
                holds.append(f"{rel}: unresolved conflicts block relevant Gates")
        elif name == "acceptance":
            result = data.get("result")
            if result not in {"NOT_EVALUATED", "HOLD", "CONDITIONAL", "PASS", "FAIL"}:
                errors.append(f"{rel}: invalid acceptance result")
            if result == "PASS" and not data.get("approver"):
                errors.append(f"{rel}: PASS acceptance requires named approver")
            evidence_ids = data.get("evidence_ids")
            if not isinstance(evidence_ids, list) or not evidence_ids:
                holds.append(f"{rel}: acceptance has no evidence_ids")
    process_case = loaded_records.get("process_case")
    property_method = loaded_records.get("property_method")
    if process_case and property_method and process_case.get("property_method") != property_method:
        errors.append(
            "process_case property_method disagrees with the package property_method record"
        )
    approvals = manifest.get("approvals")
    package_approver = approvals.get("package_approver") if isinstance(approvals, dict) else None
    if not isinstance(package_approver, str) or not package_approver.strip():
        holds.append("package has no named package approver")
    status = "FAIL" if errors else "HOLD" if holds else "PASS"
    return {
        "root": str(root),
        "status": status,
        "pass": status == "PASS",
        "errors": sorted(set(errors)),
        "holds": sorted(set(holds)),
    }
