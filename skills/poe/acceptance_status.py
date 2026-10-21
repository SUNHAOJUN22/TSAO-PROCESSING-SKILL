"""Derive software, engineering, and HSE decision tracks independently.

Software integrity is not engineering acceptance. Engineering/HSE PASS may be
produced only from qualified, decision-use evidence bound by SHA-256 and a
named approver. Missing or intermediate records remain HOLD/NOT_EVALUATED.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from tsao.decision_status import aggregate_status
from tsao.json_contract import loads_strict

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_INTERMEDIATE = frozenset({"HOLD", "CONDITIONAL", "NOT_EVALUATED"})
_ALLOWED = frozenset({"PASS", "FAIL", *_INTERMEDIATE})


def _status(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().upper().replace("-", "_").replace(" ", "_")
    return normalized if normalized in _ALLOWED else None


def _string_list(value: object) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _evidence_index(ledger: object) -> tuple[dict[str, Mapping[str, Any]], set[str]]:
    if ledger is None:
        return {}, set()
    if not isinstance(ledger, Mapping) or not isinstance(ledger.get("evidence"), list):
        return {}, {"INVALID_EVIDENCE_LEDGER"}
    index: dict[str, Mapping[str, Any]] = {}
    errors: set[str] = set()
    for row in ledger["evidence"]:
        if not isinstance(row, Mapping):
            errors.add("INVALID_EVIDENCE_RECORD")
            continue
        evidence_id = row.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            errors.add("INVALID_EVIDENCE_ID")
        elif evidence_id.strip() in index:
            errors.add("DUPLICATE_EVIDENCE_ID")
        else:
            index[evidence_id.strip()] = row
    return index, errors


def _qualified_evidence(
    evidence_id: str, index: Mapping[str, Mapping[str, Any]], artifact_root: Path | None
) -> tuple[bool, str | None]:
    record = index.get(evidence_id)
    if record is None:
        return False, "UNKNOWN_EVIDENCE_REFERENCE"
    if record.get("status") != "QUALIFIED":
        return False, "EVIDENCE_NOT_QUALIFIED"
    if record.get("decision_use") is not True:
        return False, "EVIDENCE_NOT_AUTHORIZED_FOR_DECISION_USE"
    artifact_sha256 = record.get("artifact_sha256")
    if not isinstance(artifact_sha256, str) or not _SHA256.fullmatch(artifact_sha256):
        return False, "EVIDENCE_NOT_HASH_BOUND"
    approver = record.get("approver")
    if not isinstance(approver, str) or not approver.strip():
        return False, "EVIDENCE_HAS_NO_NAMED_APPROVER"
    if artifact_root is None:
        return False, "EVIDENCE_ARTIFACT_NOT_VERIFIED"
    artifact = _safe_record_path(artifact_root, record.get("artifact_path"))
    if artifact is None:
        return False, "EVIDENCE_ARTIFACT_UNAVAILABLE"
    try:
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    except OSError:
        return False, "EVIDENCE_ARTIFACT_UNAVAILABLE"
    if digest != artifact_sha256:
        return False, "EVIDENCE_ARTIFACT_HASH_MISMATCH"
    return True, None


def _evaluate_rows(
    rows: object,
    *,
    track: str,
    evidence_index: Mapping[str, Mapping[str, Any]],
    artifact_root: Path | None,
) -> tuple[str, set[str], set[str]]:
    reasons: set[str] = set()
    evidence_refs: set[str] = set()
    if not isinstance(rows, list) or not rows:
        return "NOT_EVALUATED", {f"{track}_RECORDS_MISSING"}, evidence_refs

    observed: list[str] = []
    row_ids: set[str] = set()
    for _index, row in enumerate(rows, start=1):
        if not isinstance(row, Mapping):
            reasons.add(f"{track}_ROW_NOT_OBJECT")
            observed.append("FAIL")
            continue
        id_field = (
            "requirement_id"
            if track == "REQUIREMENT"
            else "hazard_id"
            if track == "HSE"
            else "criterion_id"
        )
        row_id = row.get(id_field)
        if row_id is not None:
            if not isinstance(row_id, str) or not row_id.strip() or row_id.strip() in row_ids:
                reasons.add(f"{track}_INVALID_OR_DUPLICATE_ID")
                observed.append("FAIL")
                continue
            row_ids.add(row_id.strip())
        if "status" in row and "result" in row and _status(row["status"]) != _status(row["result"]):
            reasons.add(f"{track}_CONFLICTING_STATUS")
            observed.append("FAIL")
            continue
        row_status = _status(row.get("status") if "status" in row else row.get("result"))
        if row_status is None:
            reasons.add(f"{track}_INVALID_STATUS")
            observed.append("FAIL")
            continue
        observed.append(row_status)
        if row_status == "PASS":
            approver = row.get("approver")
            if not isinstance(approver, str) or not approver.strip():
                reasons.add(f"{track}_PASS_HAS_NO_APPROVER")
                observed[-1] = "HOLD"
            raw_refs = row.get("evidence_ids")
            refs = _string_list(raw_refs)
            if (
                not isinstance(raw_refs, list)
                or len(refs) != len(raw_refs)
                or len(set(refs)) != len(refs)
            ):
                reasons.add(f"{track}_INVALID_EVIDENCE_REFERENCES")
                observed[-1] = "FAIL"
                continue
            if not refs:
                reasons.add(f"{track}_PASS_HAS_NO_EVIDENCE")
                observed[-1] = "HOLD"
            for ref in refs:
                evidence_refs.add(ref)
                qualified, reason = _qualified_evidence(ref, evidence_index, artifact_root)
                if not qualified:
                    reasons.add(reason or f"{track}_EVIDENCE_INVALID")
                    observed[-1] = "HOLD"
        elif row_status == "FAIL":
            reasons.add(f"{track}_EXPLICIT_FAIL")
        else:
            reasons.add(f"{track}_{row_status}")

    result = aggregate_status(observed)
    return ("HOLD" if result in _INTERMEDIATE else result), reasons, evidence_refs


def _software_status(result: object) -> tuple[str, set[str]]:
    if result is None or result == {}:
        return "NOT_EVALUATED", {"SOFTWARE_RESULT_MISSING"}
    if not isinstance(result, Mapping):
        return "FAIL", {"SOFTWARE_RESULT_INVALID"}
    state = _status(result.get("status"))
    errors, holds = result.get("errors"), result.get("holds")
    if state is None or not isinstance(errors, list) or not isinstance(holds, list):
        return "FAIL", {"SOFTWARE_RESULT_INVALID"}
    if any(not isinstance(value, str) or not value.strip() for value in (*errors, *holds)):
        return "FAIL", {"SOFTWARE_RESULT_INVALID"}
    if "pass" in result and not isinstance(result["pass"], bool):
        return "FAIL", {"SOFTWARE_RESULT_INVALID"}
    if state == "FAIL" or errors or result.get("pass") is False and state == "PASS":
        return "FAIL", {"SOFTWARE_INTEGRITY_ERRORS"}
    if holds or state in _INTERMEDIATE:
        return ("NOT_EVALUATED" if state == "NOT_EVALUATED" and not holds else "HOLD"), {
            "SOFTWARE_NOT_PASSED"
        }
    return "PASS", set()


def derive_decision_tracks(
    *,
    software_result: object,
    requirement_trace: object,
    acceptance: object,
    evidence_ledger: object,
    hse: object = None,
    artifact_root: Path | None = None,
) -> dict[str, Any]:
    """Derive independent status tracks from machine evidence."""

    software_integrity_status, reasons = _software_status(software_result)
    evidence_index, evidence_errors = _evidence_index(evidence_ledger)
    reasons.update(evidence_errors)
    requirements = (
        requirement_trace.get("requirements") if isinstance(requirement_trace, Mapping) else None
    )
    requirement_status, requirement_reasons, requirement_refs = _evaluate_rows(
        requirements,
        track="REQUIREMENT",
        evidence_index=evidence_index,
        artifact_root=artifact_root,
    )

    acceptance_rows: object
    if isinstance(acceptance, Mapping):
        acceptance_rows = [
            {
                **acceptance,
                "status": acceptance.get("status", acceptance.get("result")),
                "approver": acceptance.get("approver"),
                "evidence_ids": acceptance.get("evidence_ids"),
            }
        ]
    else:
        acceptance_rows = None
    acceptance_status, acceptance_reasons, acceptance_refs = _evaluate_rows(
        acceptance_rows,
        track="ACCEPTANCE",
        evidence_index=evidence_index,
        artifact_root=artifact_root,
    )

    reasons.update(requirement_reasons)
    reasons.update(acceptance_reasons)
    engineering_status = aggregate_status(
        (requirement_status, acceptance_status, "FAIL" if evidence_errors else "PASS")
    )

    hse_rows = hse.get("hazards") if isinstance(hse, Mapping) else hse
    hse_status, hse_reasons, hse_refs = _evaluate_rows(
        hse_rows,
        track="HSE",
        evidence_index=evidence_index,
        artifact_root=artifact_root,
    )
    reasons.update(hse_reasons)

    overall = aggregate_status((software_integrity_status, engineering_status, hse_status))
    if overall in _INTERMEDIATE:
        overall = "HOLD"

    evidence_refs = sorted(requirement_refs | acceptance_refs | hse_refs)
    return {
        "software_integrity_status": software_integrity_status,
        "engineering_acceptance_status": engineering_status,
        "hse_status": hse_status,
        "qualification_scope": (
            "SOFTWARE_AND_ENGINEERING_AND_HSE"
            if overall == "PASS"
            else "SOFTWARE_INTEGRITY_ONLY"
            if software_integrity_status == "PASS"
            else "NO_QUALIFIED_SCOPE"
        ),
        "reason_codes": sorted(reasons),
        "evidence_refs": evidence_refs,
        "overall_status": overall,
        "pass": overall == "PASS",
        "artifact_verification": "LOCAL_BYTES_SHA256"
        if artifact_root is not None
        else "NOT_EVALUATED",
        "truth_boundary": "SOFTWARE_PASS_DOES_NOT_IMPLY_ENGINEERING_OR_HSE_APPROVAL",
    }


def _safe_record_path(root: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/"):
        return None
    pure = PurePosixPath(value)
    if not pure.parts or pure.is_absolute() or ".." in pure.parts or pure.parts[0].endswith(":"):
        return None
    candidate = root
    for part in pure.parts:
        candidate /= part
        if candidate.is_symlink():
            return None
    candidate = candidate.resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate if candidate.is_file() and not candidate.is_symlink() else None


def _load(path: Path | None) -> object:
    if path is None:
        return None
    try:
        return loads_strict(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return None


def derive_decision_tracks_from_root(
    root: Path, software_result: Mapping[str, Any]
) -> dict[str, Any]:
    """Load decision records conservatively from a package root."""

    root = Path(root)
    manifest = _load(root / "manifest.json")
    if not isinstance(manifest, Mapping):
        return derive_decision_tracks(
            software_result=software_result,
            requirement_trace=None,
            acceptance=None,
            evidence_ledger=None,
            hse=None,
        )
    structured = manifest.get("structured_records")
    if not isinstance(structured, Mapping):
        structured = {}

    def record(name: str) -> object:
        return _load(_safe_record_path(root, structured.get(name)))

    return derive_decision_tracks(
        software_result=software_result,
        requirement_trace=record("requirement_trace"),
        acceptance=record("acceptance"),
        evidence_ledger=record("evidence_ledger"),
        hse=record("hse"),
        artifact_root=root,
    )
