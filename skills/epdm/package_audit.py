from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from tsao.process_package import validate_process_package

from .qualification import validate_epdm_case


def _epdm_evidence_ids(value: object) -> set[str]:
    """Collect every EPDM evidence reference, including future nested contract fields."""
    referenced: set[str] = set()
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key == "evidence_id" and isinstance(item, str) and item.strip():
                referenced.add(item)
                continue
            if key.endswith("evidence_ids") and isinstance(item, Sequence) and not isinstance(
                item, (str, bytes)
            ):
                referenced.update(
                    evidence_id
                    for evidence_id in item
                    if isinstance(evidence_id, str) and evidence_id.strip()
                )
                continue
            referenced.update(_epdm_evidence_ids(item))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for item in value:
            referenced.update(_epdm_evidence_ids(item))
    return referenced


def _ledger_ids(ledger: object, errors: list[str]) -> set[str]:
    if not isinstance(ledger, list):
        errors.append("process package evidence_ledger must be an array")
        return set()
    known: set[str] = set()
    duplicates: set[str] = set()
    for index, item in enumerate(ledger):
        if not isinstance(item, dict):
            errors.append(f"evidence_ledger[{index}] must be an object")
            continue
        evidence_id = item.get("evidence_id")
        if not isinstance(evidence_id, str) or not evidence_id.strip():
            errors.append(f"evidence_ledger[{index}].evidence_id is required")
            continue
        if evidence_id in known:
            duplicates.add(evidence_id)
        known.add(evidence_id)
    if duplicates:
        errors.append(f"process package evidence ledger contains duplicate IDs: {sorted(duplicates)}")
    return known


def _audit_epdm_process_package(package: object) -> dict[str, Any]:
    if not isinstance(package, dict):
        return {
            "status": "FAIL",
            "pass": False,
            "errors": ["package root must be an object"],
            "holds": [],
        }
    generic = validate_process_package(package)
    case_payload = package.get("epdm_case")
    case = validate_epdm_case(case_payload)
    errors = [f"process package: {item}" for item in generic["errors"]] + [
        f"EPDM case: {item}" for item in case["errors"]
    ]
    holds = [f"process package: {item}" for item in generic["holds"]] + [
        f"EPDM case: {item}" for item in case["holds"]
    ]
    family = package.get("process_family")
    if not isinstance(family, str) or not any(
        token in family.casefold() for token in ("epdm", "epm", "ethylene propylene")
    ):
        errors.append("process package family is not identified as EPM/EPDM")

    known = _ledger_ids(package.get("evidence_ledger"), errors)
    if isinstance(case_payload, dict):
        missing = sorted(_epdm_evidence_ids(case_payload) - known)
        if missing:
            errors.append(f"EPDM case references evidence absent from package ledger: {missing}")

    status = "FAIL" if errors else "HOLD" if holds else "PASS"
    return {
        "status": status,
        "pass": status == "PASS",
        "errors": sorted(set(errors)),
        "holds": sorted(set(holds)),
        "generic": generic,
        "epdm": case,
        "scientific_technical_approval": "NOT_EVALUATED",
        "engineering_design_approval": "NOT_EVALUATED",
        "customer_qualification": "NOT_EVALUATED",
    }


def audit_epdm_process_package(package: object) -> dict[str, Any]:
    """Fail closed for malformed package payloads without leaking internal exceptions."""
    try:
        return _audit_epdm_process_package(package)
    except Exception as exc:  # defensive public boundary
        return {
            "status": "FAIL",
            "pass": False,
            "errors": [f"unexpected EPDM package audit failure: {type(exc).__name__}"],
            "holds": [],
            "scientific_technical_approval": "NOT_EVALUATED",
            "engineering_design_approval": "NOT_EVALUATED",
            "customer_qualification": "NOT_EVALUATED",
        }
