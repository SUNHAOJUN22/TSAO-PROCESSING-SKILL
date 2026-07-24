from __future__ import annotations

from typing import Any

from tsao.process_package import validate_process_package

from .qualification import validate_epdm_case


def _epdm_evidence_ids(case: dict[str, Any]) -> set[str]:
    referenced: set[str] = set()
    catalyst = case.get("catalyst")
    if isinstance(catalyst, dict) and isinstance(catalyst.get("active_site_evidence_ids"), list):
        referenced.update(item for item in catalyst["active_site_evidence_ids"] if isinstance(item, str))
    bridge = case.get("product_bridge")
    if isinstance(bridge, dict):
        for record in bridge.values():
            if isinstance(record, dict) and isinstance(record.get("evidence_ids"), list):
                referenced.update(item for item in record["evidence_ids"] if isinstance(item, str))
    return referenced


def audit_epdm_process_package(package: object) -> dict[str, Any]:
    if not isinstance(package, dict):
        return {"status": "FAIL", "pass": False, "errors": ["package root must be an object"], "holds": []}
    generic = validate_process_package(package)
    case_payload = package.get("epdm_case")
    case = validate_epdm_case(case_payload)
    errors = [f"process package: {item}" for item in generic["errors"]] + [f"EPDM case: {item}" for item in case["errors"]]
    holds = [f"process package: {item}" for item in generic["holds"]] + [f"EPDM case: {item}" for item in case["holds"]]
    family = package.get("process_family")
    if not isinstance(family, str) or not any(token in family.casefold() for token in ("epdm", "epm", "ethylene propylene")):
        errors.append("process package family is not identified as EPM/EPDM")
    ledger = package.get("evidence_ledger")
    known = {item.get("evidence_id") for item in ledger if isinstance(ledger, list) and isinstance(item, dict) and isinstance(item.get("evidence_id"), str)} if isinstance(ledger, list) else set()
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
