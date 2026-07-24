from __future__ import annotations

import math
from copy import deepcopy
from typing import Any

_BOUNDARY_NODES = {"BOUNDARY_IN", "BOUNDARY_OUT", "ENVIRONMENT"}
_ACCEPTANCE_STATES = {"NOT_EVALUATED", "HOLD", "CONDITIONAL", "PASS", "FAIL"}
_EVIDENCE_STATES = {"REPORTED", "CALCULATED", "QUALIFIED", "HOLD", "SUPERSEDED", "RETRACTED"}


def _finite(value: object, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _records(value: object, label: str, errors: list[str]) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return []
    records: list[dict[str, Any]] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, dict):
            errors.append(f"{label} row {index} must be an object")
        else:
            records.append(item)
    return records


def _unique_ids(records: list[dict[str, Any]], field: str, label: str, errors: list[str]) -> set[str]:
    seen: set[str] = set()
    for index, record in enumerate(records, start=1):
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label} row {index} has invalid {field}")
            continue
        if value in seen:
            errors.append(f"duplicate {label} {field}: {value}")
        seen.add(value)
    return seen


def process_package_template(process_family: str) -> dict[str, Any]:
    if not isinstance(process_family, str) or not process_family.strip():
        raise ValueError("process_family must be a non-empty string")
    return {
        "package_id": "TEMPLATE-NOT-A-DESIGN-BASIS",
        "process_family": process_family.strip(),
        "status": "NOT_EVALUATED",
        "tolerances": {"composition_abs": 1e-6, "mass_relative": 1e-4, "energy_relative": 1e-3},
        "design_basis": {
            "basis_version": "DRAFT",
            "capacity_kg_h": 1.0,
            "operating_hours_h_y": 1.0,
            "components": ["COMPONENT-A"],
        },
        "streams": [],
        "equipment": [],
        "utilities": [],
        "controls": [],
        "hse": [],
        "evidence_ledger": [],
        "acceptance": [],
        "approvals": {},
    }


def validate_process_package(package: object) -> dict[str, Any]:
    errors: list[str] = []
    holds: list[str] = []
    if not isinstance(package, dict):
        return {"status": "FAIL", "pass": False, "errors": ["package root must be an object"], "holds": []}

    package_id = package.get("package_id")
    process_family = package.get("process_family")
    if not isinstance(package_id, str) or not package_id.strip():
        errors.append("package_id is required")
    if not isinstance(process_family, str) or not process_family.strip():
        errors.append("process_family is required")
    if package_id == "TEMPLATE-NOT-A-DESIGN-BASIS":
        holds.append("template package is not an approved design basis")

    tolerances = package.get("tolerances", {})
    if not isinstance(tolerances, dict):
        errors.append("tolerances must be an object")
        tolerances = {}
    try:
        composition_tol = _finite(tolerances.get("composition_abs", 1e-6), "composition tolerance")
        mass_tol = _finite(tolerances.get("mass_relative", 1e-4), "mass tolerance")
        energy_tol = _finite(tolerances.get("energy_relative", 1e-3), "energy tolerance")
        if min(composition_tol, mass_tol, energy_tol) < 0:
            raise ValueError("tolerances must be non-negative")
    except ValueError as exc:
        errors.append(str(exc))
        composition_tol, mass_tol, energy_tol = 1e-6, 1e-4, 1e-3

    design_basis = package.get("design_basis")
    components: set[str] = set()
    if not isinstance(design_basis, dict):
        errors.append("design_basis must be an object")
    else:
        for field in ("basis_version", "components"):
            if field not in design_basis:
                errors.append(f"design_basis.{field} is required")
        try:
            if _finite(design_basis.get("capacity_kg_h"), "design capacity") <= 0:
                errors.append("design capacity must be positive")
            if _finite(design_basis.get("operating_hours_h_y"), "operating hours") <= 0:
                errors.append("operating hours must be positive")
        except ValueError as exc:
            errors.append(str(exc))
        raw_components = design_basis.get("components")
        if not isinstance(raw_components, list) or not raw_components:
            errors.append("design_basis.components must be a non-empty list")
        else:
            for item in raw_components:
                if not isinstance(item, str) or not item.strip():
                    errors.append("design_basis.components contains an invalid component")
                elif item in components:
                    errors.append(f"duplicate design component: {item}")
                else:
                    components.add(item)

    streams = _records(package.get("streams"), "streams", errors)
    equipment = _records(package.get("equipment"), "equipment", errors)
    utilities = _records(package.get("utilities", []), "utilities", errors)
    controls = _records(package.get("controls", []), "controls", errors)
    hazards = _records(package.get("hse", []), "hse", errors)
    evidence = _records(package.get("evidence_ledger", []), "evidence_ledger", errors)
    acceptance = _records(package.get("acceptance", []), "acceptance", errors)

    stream_ids = _unique_ids(streams, "stream_id", "stream", errors)
    equipment_ids = _unique_ids(equipment, "equipment_id", "equipment", errors)
    _unique_ids(utilities, "utility_id", "utility", errors)
    _unique_ids(controls, "loop_id", "control", errors)
    _unique_ids(hazards, "hazard_id", "hazard", errors)
    evidence_ids = _unique_ids(evidence, "evidence_id", "evidence", errors)
    _unique_ids(acceptance, "criterion_id", "acceptance", errors)

    evidence_status: dict[str, str] = {}
    for record in evidence:
        identifier = record.get("evidence_id")
        state = record.get("status")
        if isinstance(identifier, str):
            if state not in _EVIDENCE_STATES:
                errors.append(f"evidence {identifier} has invalid status")
            else:
                evidence_status[identifier] = state
        if not record.get("locator") or not record.get("applicability"):
            holds.append(f"evidence {identifier or '<unknown>'} lacks locator or applicability")

    stream_by_id: dict[str, dict[str, Any]] = {}
    for stream in streams:
        identifier = stream.get("stream_id")
        if isinstance(identifier, str):
            stream_by_id[identifier] = stream
        source = stream.get("source")
        destination = stream.get("destination")
        for label, node in (("source", source), ("destination", destination)):
            if not isinstance(node, str) or not node.strip():
                errors.append(f"stream {identifier or '<unknown>'} has invalid {label}")
            elif node not in equipment_ids and node not in _BOUNDARY_NODES:
                errors.append(f"stream {identifier or '<unknown>'} references unknown {label}: {node}")
        try:
            total_mass = _finite(stream.get("total_mass_kg_h"), f"stream {identifier} mass flow")
            _finite(stream.get("enthalpy_kW"), f"stream {identifier} enthalpy")
            if total_mass < 0:
                errors.append(f"stream {identifier} mass flow must be non-negative")
        except ValueError as exc:
            errors.append(str(exc))
            total_mass = 0.0
        composition = stream.get("composition")
        if not isinstance(composition, dict) or not composition:
            errors.append(f"stream {identifier} composition must be a non-empty object")
        else:
            total_fraction = 0.0
            for component, fraction in composition.items():
                if component not in components:
                    errors.append(f"stream {identifier} uses undeclared component: {component}")
                try:
                    value = _finite(fraction, f"stream {identifier} composition {component}")
                    if value < 0:
                        errors.append(f"stream {identifier} composition {component} must be non-negative")
                    total_fraction += value
                except ValueError as exc:
                    errors.append(str(exc))
            if abs(total_fraction - 1.0) > composition_tol:
                errors.append(f"stream {identifier} composition sum is {total_fraction:.12g}, expected 1")
        refs = stream.get("evidence_ids", [])
        if not isinstance(refs, list) or not refs:
            holds.append(f"stream {identifier} has no evidence_ids")
        else:
            for ref in refs:
                if ref not in evidence_ids:
                    errors.append(f"stream {identifier} references unknown evidence: {ref}")

    mass_errors: dict[str, float] = {}
    energy_errors: dict[str, float] = {}
    for item in equipment:
        identifier = item.get("equipment_id")
        if not isinstance(identifier, str):
            continue
        inlet_ids = item.get("inlet_stream_ids")
        outlet_ids = item.get("outlet_stream_ids")
        if not isinstance(inlet_ids, list) or not isinstance(outlet_ids, list):
            errors.append(f"equipment {identifier} inlet/outlet stream IDs must be lists")
            continue
        for ref in [*inlet_ids, *outlet_ids]:
            if ref not in stream_ids:
                errors.append(f"equipment {identifier} references unknown stream: {ref}")
        if any(ref not in stream_by_id for ref in [*inlet_ids, *outlet_ids]):
            continue
        mass_in = sum(float(stream_by_id[ref]["total_mass_kg_h"]) for ref in inlet_ids)
        mass_out = sum(float(stream_by_id[ref]["total_mass_kg_h"]) for ref in outlet_ids)
        mass_scale = max(abs(mass_in), abs(mass_out), 1.0)
        mass_error = abs(mass_in - mass_out) / mass_scale
        mass_errors[identifier] = mass_error
        if mass_error > mass_tol:
            errors.append(f"equipment {identifier} mass balance relative error {mass_error:.6g} exceeds {mass_tol:.6g}")
        enthalpy_in = sum(float(stream_by_id[ref]["enthalpy_kW"]) for ref in inlet_ids)
        enthalpy_out = sum(float(stream_by_id[ref]["enthalpy_kW"]) for ref in outlet_ids)
        try:
            duty = _finite(item.get("duty_kW", 0.0), f"equipment {identifier} duty")
        except ValueError as exc:
            errors.append(str(exc))
            duty = 0.0
        energy_scale = max(abs(enthalpy_in) + abs(duty), abs(enthalpy_out), 1.0)
        energy_error = abs(enthalpy_in + duty - enthalpy_out) / energy_scale
        energy_errors[identifier] = energy_error
        if energy_error > energy_tol:
            errors.append(f"equipment {identifier} energy balance relative error {energy_error:.6g} exceeds {energy_tol:.6g}")
        if item.get("design_status") not in _ACCEPTANCE_STATES:
            holds.append(f"equipment {identifier} design_status is not evaluated")

    for utility in utilities:
        identifier = utility.get("utility_id")
        try:
            if _finite(utility.get("consumption"), f"utility {identifier} consumption") < 0:
                errors.append(f"utility {identifier} consumption must be non-negative")
        except ValueError as exc:
            errors.append(str(exc))
        if not utility.get("unit"):
            errors.append(f"utility {identifier} unit is required")

    for loop in controls:
        identifier = loop.get("loop_id")
        for field in ("controlled_variable", "manipulated_variable", "measurement_tag", "final_element_tag"):
            if not isinstance(loop.get(field), str) or not loop[field].strip():
                holds.append(f"control {identifier} lacks {field}")
        if loop.get("status") not in _ACCEPTANCE_STATES:
            holds.append(f"control {identifier} status is not evaluated")

    for hazard in hazards:
        identifier = hazard.get("hazard_id")
        safeguards = hazard.get("safeguards")
        if not isinstance(safeguards, list) or not safeguards:
            errors.append(f"hazard {identifier} has no safeguards")
        if hazard.get("status") != "PASS":
            holds.append(f"hazard {identifier} is not closed")

    if not acceptance:
        holds.append("package has no acceptance criteria")
    for criterion in acceptance:
        identifier = criterion.get("criterion_id")
        state = criterion.get("status")
        if state not in _ACCEPTANCE_STATES:
            errors.append(f"acceptance {identifier} has invalid status")
            continue
        refs = criterion.get("evidence_ids")
        if not isinstance(refs, list) or not refs:
            holds.append(f"acceptance {identifier} has no evidence_ids")
        else:
            for ref in refs:
                if ref not in evidence_ids:
                    errors.append(f"acceptance {identifier} references unknown evidence: {ref}")
                elif state == "PASS" and evidence_status.get(ref) != "QUALIFIED":
                    errors.append(f"acceptance {identifier} PASS uses non-qualified evidence: {ref}")
        if state == "PASS" and not criterion.get("approver"):
            errors.append(f"acceptance {identifier} PASS requires named approver")
        elif state != "PASS":
            holds.append(f"acceptance {identifier} is {state}")

    approvals = package.get("approvals")
    if not isinstance(approvals, dict):
        holds.append("package approvals are missing")
    else:
        for role in ("package_approver", "process", "controls", "hse"):
            if not isinstance(approvals.get(role), str) or not approvals[role].strip():
                holds.append(f"package approval missing: {role}")

    status = "FAIL" if errors else "HOLD" if holds else "PASS"
    return {
        "status": status,
        "pass": status == "PASS",
        "errors": sorted(set(errors)),
        "holds": sorted(set(holds)),
        "metrics": {
            "stream_count": len(streams),
            "equipment_count": len(equipment),
            "acceptance_count": len(acceptance),
            "max_mass_balance_relative_error": max(mass_errors.values(), default=0.0),
            "max_energy_balance_relative_error": max(energy_errors.values(), default=0.0),
        },
    }


def normalized_package_copy(package: dict[str, Any]) -> dict[str, Any]:
    """Return a defensive copy for adapters without mutating caller-owned data."""
    if not isinstance(package, dict):
        raise ValueError("package must be an object")
    return deepcopy(package)
