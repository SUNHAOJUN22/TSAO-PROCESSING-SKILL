from __future__ import annotations

import json
import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from .contracts import SI_UNIT_DIMENSIONS, GateDecision, GateReasonCode

SCHEMA_VERSION = "2.0.0"
SEMANTIC_VALIDATOR_VERSION = "1.0.0-phase-a1"
_TERMINAL_EVIDENCE = {"RETRACTED", "SUPERSEDED"}
_PROVISIONAL_EVIDENCE = {"REPORTED", "CALCULATED", "HOLD"}


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    severity: str
    reason_code: GateReasonCode
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "reason_code": self.reason_code.value,
            "path": self.path,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class V2ValidationResult:
    decision: GateDecision
    issues: tuple[ValidationIssue, ...]
    schema_version: str = SCHEMA_VERSION
    semantic_validator_version: str = SEMANTIC_VALIDATOR_VERSION

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "ERROR")

    @property
    def holds(self) -> tuple[ValidationIssue, ...]:
        return tuple(issue for issue in self.issues if issue.severity == "HOLD")

    def as_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "pass": self.decision == GateDecision.PASS,
            "schema_version": self.schema_version,
            "semantic_validator_version": self.semantic_validator_version,
            "errors": [issue.as_dict() for issue in self.errors],
            "holds": [issue.as_dict() for issue in self.holds],
            "internal_error": False,
            "v2_numerical_execution": "NOT_IMPLEMENTED_PHASE_A1",
            "scientific_technical_approval": "NOT_EVALUATED",
            "engineering_design_approval": "NOT_EVALUATED",
        }


def _schema_directory(schema_dir: Path | None) -> Path:
    return schema_dir or Path(__file__).with_name("schemas")


def _schema_validator(schema_name: str, schema_dir: Path | None = None) -> Draft202012Validator:
    directory = _schema_directory(schema_dir)
    schemas: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.schema.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("$id"), str):
            schemas.append(payload)
    registry = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema)) for schema in schemas
    )
    target = next(
        (schema for schema in schemas if schema["$id"].endswith("/" + schema_name)),
        None,
    )
    if target is None:
        raise FileNotFoundError(schema_name)
    return Draft202012Validator(target, registry=registry)


def validate_schema_instance(
    instance: object,
    schema_name: str,
    *,
    schema_dir: Path | None = None,
) -> tuple[ValidationIssue, ...]:
    validator = _schema_validator(schema_name, schema_dir)
    issues: list[ValidationIssue] = []
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path)):
        path = "$" + "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path
        )
        issues.append(
            ValidationIssue(
                "ERROR",
                GateReasonCode.SEMANTIC_REFERENCE_UNRESOLVED,
                path,
                error.message,
            )
        )
    return tuple(issues)


def _index(
    records: object,
    id_field: str,
    path: str,
    issues: list[ValidationIssue],
) -> dict[str, dict[str, Any]]:
    if not isinstance(records, list):
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for position, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        identifier = record.get(id_field)
        if not isinstance(identifier, str):
            continue
        if identifier in indexed:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    GateReasonCode.SEMANTIC_REFERENCE_UNRESOLVED,
                    f"{path}[{position}].{id_field}",
                    f"duplicate identifier: {identifier}",
                )
            )
        else:
            indexed[identifier] = record
    return indexed


def _require_reference(
    identifier: object,
    registry: Mapping[str, object],
    path: str,
    label: str,
    issues: list[ValidationIssue],
) -> None:
    if not isinstance(identifier, str) or identifier not in registry:
        issues.append(
            ValidationIssue(
                "ERROR",
                GateReasonCode.SEMANTIC_REFERENCE_UNRESOLVED,
                path,
                f"unresolved {label} reference: {identifier!r}",
            )
        )


def _collect_evidence_references(value: object, path: str = "$") -> dict[str, set[str]]:
    references: dict[str, set[str]] = defaultdict(set)
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key == "evidence_ledger":
                continue
            child = f"{path}.{key}"
            if key == "evidence_id" and isinstance(item, str):
                references[item].add(child)
            elif key.endswith("evidence_ids") and isinstance(item, Sequence) and not isinstance(
                item, (str, bytes)
            ):
                for index, identifier in enumerate(item):
                    if isinstance(identifier, str):
                        references[identifier].add(f"{child}[{index}]")
            else:
                nested = _collect_evidence_references(item, child)
                for identifier, paths in nested.items():
                    references[identifier].update(paths)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, item in enumerate(value):
            nested = _collect_evidence_references(item, f"{path}[{index}]")
            for identifier, paths in nested.items():
                references[identifier].update(paths)
    return references


def _validate_ranges(
    domains: Mapping[str, dict[str, Any]], issues: list[ValidationIssue]
) -> None:
    for domain_id, domain in domains.items():
        for field in (
            "temperature_K",
            "pressure_Pa",
            "ethylene_fraction",
            "propylene_fraction",
            "diene_fraction",
            "hydrogen_ratio",
        ):
            bounds = domain.get(field)
            if isinstance(bounds, list) and len(bounds) == 2 and bounds[0] > bounds[1]:
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        GateReasonCode.INVALID_UNIT_BASIS,
                        f"$.applicability_domains[{domain_id}].{field}",
                        "lower bound exceeds upper bound",
                    )
                )


def _validate_evidence(
    project: Mapping[str, Any],
    evidence: Mapping[str, dict[str, Any]],
    issues: list[ValidationIssue],
) -> None:
    fixture = project.get("extensions", {}).get("case_kind") == "SYNTHETIC_REFERENCE_TEST"
    references = _collect_evidence_references(project)
    for evidence_id, paths in sorted(references.items()):
        record = evidence.get(evidence_id)
        path = sorted(paths)[0]
        if record is None:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    GateReasonCode.MISSING_EVIDENCE,
                    path,
                    f"evidence reference is absent from ledger: {evidence_id}",
                )
            )
            continue
        status = record.get("status")
        if status in _TERMINAL_EVIDENCE:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    GateReasonCode.MISSING_EVIDENCE,
                    path,
                    f"evidence {evidence_id} is terminally invalid: {status}",
                )
            )
        elif status in _PROVISIONAL_EVIDENCE:
            issues.append(
                ValidationIssue(
                    "HOLD",
                    GateReasonCode.MISSING_EVIDENCE,
                    path,
                    f"evidence {evidence_id} is not QUALIFIED: {status}",
                )
            )
        source_type = record.get("source_type")
        if source_type == "ASSUMED":
            issues.append(
                ValidationIssue(
                    "HOLD",
                    GateReasonCode.MISSING_EVIDENCE,
                    path,
                    f"assumed evidence {evidence_id} cannot support an engineering-use claim",
                )
            )
        if source_type == "SYNTHETIC_FIXTURE" and not fixture:
            issues.append(
                ValidationIssue(
                    "HOLD",
                    GateReasonCode.MISSING_EVIDENCE,
                    path,
                    f"synthetic fixture evidence {evidence_id} cannot qualify a project case",
                )
            )


def _validate_units(project: Mapping[str, Any], issues: list[ValidationIssue]) -> None:
    def visit(value: object, path: str) -> None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                child = f"{path}.{key}"
                if key in {"unit", "uncertainty_unit"} and item is not None:
                    if item not in SI_UNIT_DIMENSIONS:
                        issues.append(
                            ValidationIssue(
                                "ERROR",
                                GateReasonCode.INVALID_UNIT_BASIS,
                                child,
                                f"unit is outside the SI allowlist: {item!r}",
                            )
                        )
                visit(item, child)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            for index, item in enumerate(value):
                visit(item, f"{path}[{index}]")
        elif isinstance(value, float) and not math.isfinite(value):
            issues.append(
                ValidationIssue(
                    "ERROR",
                    GateReasonCode.INVALID_UNIT_BASIS,
                    path,
                    "non-finite numerical value",
                )
            )

    visit(project, "$")


def _validate_dataset_leakage(
    datasets: Mapping[str, dict[str, Any]], issues: list[ValidationIssue]
) -> None:
    identities: dict[str, dict[str, set[str]]] = {
        "observation_id": defaultdict(set),
        "experiment_id": defaultdict(set),
        "experiment_group_id": defaultdict(set),
    }
    for dataset in datasets.values():
        role = dataset.get("role")
        for target in dataset.get("targets", []):
            if not isinstance(target, dict):
                continue
            use = target.get("use", role)
            for field in identities:
                identifier = target.get(field)
                if isinstance(identifier, str):
                    identities[field][identifier].add(str(use))
    validation_roles = {"VALIDATION", "HOLDOUT"}
    for field, values in identities.items():
        for identifier, roles in values.items():
            if "CALIBRATION" in roles and roles & validation_roles:
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        GateReasonCode.DATA_LEAKAGE,
                        f"$.datasets.{field}",
                        f"{field} {identifier} appears in calibration and validation/holdout",
                    )
                )


def _validate_calibration_plans(
    plans: Mapping[str, dict[str, Any]],
    parameters: Mapping[str, dict[str, Any]],
    targets: Mapping[str, dict[str, Any]],
    issues: list[ValidationIssue],
) -> None:
    for plan_id, plan in plans.items():
        bindings = plan.get("parameter_bindings", [])
        allow_grade = plan.get("allow_grade_specific_parameters") is True
        allow_reactor = plan.get("allow_reactor_specific_parameters") is True
        for index, binding in enumerate(bindings):
            if not isinstance(binding, dict):
                continue
            parameter_id = binding.get("parameter_id")
            _require_reference(
                parameter_id,
                parameters,
                f"$.calibration_plans[{plan_id}].parameter_bindings[{index}].parameter_id",
                "parameter",
                issues,
            )
            scope = binding.get("scope")
            if scope == "GRADE_CORRECTION" and not allow_grade:
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        GateReasonCode.ILLEGAL_PARAMETER_BINDING,
                        f"$.calibration_plans[{plan_id}].parameter_bindings[{index}].scope",
                        "grade-specific binding is disabled by the calibration plan",
                    )
                )
            if scope == "REACTOR_CORRECTION" and not allow_reactor:
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        GateReasonCode.ILLEGAL_PARAMETER_BINDING,
                        f"$.calibration_plans[{plan_id}].parameter_bindings[{index}].scope",
                        "reactor-specific binding is disabled by the calibration plan",
                    )
                )
        stages = plan.get("stages", [])
        if stages and stages[0].get("stage_kind") != "THERMO_RESIDENCE":
            issues.append(
                ValidationIssue(
                    "ERROR",
                    GateReasonCode.BLOCKED_BY_THERMODYNAMICS,
                    f"$.calibration_plans[{plan_id}].stages[0]",
                    "calibration must begin with THERMO_RESIDENCE",
                )
            )
        for stage_index, stage in enumerate(stages):
            if not isinstance(stage, dict):
                continue
            for target_id in stage.get("target_ids", []):
                _require_reference(
                    target_id,
                    targets,
                    f"$.calibration_plans[{plan_id}].stages[{stage_index}].target_ids",
                    "target",
                    issues,
                )
            for parameter_id in stage.get("varied_parameter_ids", []):
                _require_reference(
                    parameter_id,
                    parameters,
                    f"$.calibration_plans[{plan_id}].stages[{stage_index}].varied_parameter_ids",
                    "parameter",
                    issues,
                )
                parameter = parameters.get(parameter_id)
                if parameter and parameter.get("maturity") == "ASSUMED":
                    issues.append(
                        ValidationIssue(
                            "ERROR",
                            GateReasonCode.MISSING_EVIDENCE,
                            f"$.calibration_plans[{plan_id}].stages[{stage_index}]",
                            f"assumed parameter cannot be varied formally: {parameter_id}",
                        )
                    )


def _validate_semantics(project: Mapping[str, Any]) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    evidence = _index(project.get("evidence_ledger"), "evidence_id", "$.evidence_ledger", issues)
    domains = _index(
        project.get("applicability_domains"),
        "applicability_domain_id",
        "$.applicability_domains",
        issues,
    )
    catalysts = _index(project.get("catalyst_passports"), "catalyst_id", "$.catalyst_passports", issues)
    dienes = _index(project.get("diene_passports"), "diene_id", "$.diene_passports", issues)
    thermos = _index(project.get("thermo_passports"), "thermo_passport_id", "$.thermo_passports", issues)
    parameter_sets = _index(
        project.get("kinetic_parameter_sets"),
        "parameter_set_id",
        "$.kinetic_parameter_sets",
        issues,
    )
    state_definitions = _index(
        project.get("state_definitions"),
        "state_definition_id",
        "$.state_definitions",
        issues,
    )
    datasets = _index(project.get("datasets"), "dataset_id", "$.datasets", issues)
    plans = _index(
        project.get("calibration_plans"),
        "calibration_plan_id",
        "$.calibration_plans",
        issues,
    )
    cases = _index(project.get("cases"), "case_id", "$.cases", issues)

    _validate_ranges(domains, issues)
    _validate_evidence(project, evidence, issues)
    _validate_units(project, issues)

    all_parameters: dict[str, dict[str, Any]] = {}
    all_rate_laws: dict[str, dict[str, Any]] = {}
    for set_id, parameter_set in parameter_sets.items():
        _require_reference(parameter_set.get("catalyst_id"), catalysts, f"$.kinetic_parameter_sets[{set_id}].catalyst_id", "catalyst", issues)
        _require_reference(parameter_set.get("diene_id"), dienes, f"$.kinetic_parameter_sets[{set_id}].diene_id", "diene", issues)
        _require_reference(parameter_set.get("applicability_domain_id"), domains, f"$.kinetic_parameter_sets[{set_id}].applicability_domain_id", "applicability-domain", issues)
        local_rate_laws = _index(parameter_set.get("rate_laws"), "rate_law_id", f"$.kinetic_parameter_sets[{set_id}].rate_laws", issues)
        for identifier, record in local_rate_laws.items():
            if identifier in all_rate_laws:
                issues.append(ValidationIssue("ERROR", GateReasonCode.SEMANTIC_REFERENCE_UNRESOLVED, f"$.kinetic_parameter_sets[{set_id}].rate_laws", f"duplicate global rate-law ID: {identifier}"))
            all_rate_laws[identifier] = record
        local_parameters = _index(parameter_set.get("parameters"), "parameter_id", f"$.kinetic_parameter_sets[{set_id}].parameters", issues)
        for identifier, parameter in local_parameters.items():
            if identifier in all_parameters:
                issues.append(ValidationIssue("ERROR", GateReasonCode.SEMANTIC_REFERENCE_UNRESOLVED, f"$.kinetic_parameter_sets[{set_id}].parameters", f"duplicate global parameter ID: {identifier}"))
            all_parameters[identifier] = parameter
            _require_reference(parameter.get("rate_law_id"), local_rate_laws, f"$.kinetic_parameter_sets[{set_id}].parameters[{identifier}].rate_law_id", "rate-law", issues)
            _require_reference(parameter.get("applicability_domain_id"), domains, f"$.kinetic_parameter_sets[{set_id}].parameters[{identifier}].applicability_domain_id", "applicability-domain", issues)
            low, value, high = parameter.get("lower_bound"), parameter.get("value"), parameter.get("upper_bound")
            if all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in (low, value, high)) and not low <= value <= high:
                issues.append(ValidationIssue("ERROR", GateReasonCode.INVALID_UNIT_BASIS, f"$.kinetic_parameter_sets[{set_id}].parameters[{identifier}]", "parameter value lies outside declared bounds"))

    for catalyst_id, catalyst in catalysts.items():
        _require_reference(catalyst.get("applicability_domain_id"), domains, f"$.catalyst_passports[{catalyst_id}].applicability_domain_id", "applicability-domain", issues)
        if catalyst.get("family") == "METALLOCENE" and catalyst.get("site_model") == "EFFECTIVE_MULTISITE":
            if not catalyst.get("evidence_ids"):
                issues.append(ValidationIssue("ERROR", GateReasonCode.MISSING_EVIDENCE, f"$.catalyst_passports[{catalyst_id}].evidence_ids", "metallocene effective-multisite model requires evidence"))
        if catalyst.get("active_site_basis") == "ASSUMED":
            issues.append(ValidationIssue("HOLD", GateReasonCode.MISSING_EVIDENCE, f"$.catalyst_passports[{catalyst_id}].active_site_basis", "assumed active-site basis prevents calibration qualification"))

    for diene_id, diene in dienes.items():
        _require_reference(diene.get("applicability_domain_id"), domains, f"$.diene_passports[{diene_id}].applicability_domain_id", "applicability-domain", issues)
        if diene.get("identity") == "OTHER":
            issues.append(ValidationIssue("ERROR", GateReasonCode.UNSUPPORTED_TOPOLOGY, f"$.diene_passports[{diene_id}].identity", "OTHER diene is not supported by the frozen Phase A1 registry"))
        if not diene.get("repeat_segment_id"):
            issues.append(ValidationIssue("ERROR", GateReasonCode.UNSUPPORTED_TOPOLOGY, f"$.diene_passports[{diene_id}].repeat_segment_id", "repeat segment is required for detailed V2"))
        if not diene.get("thermo_parameter_source_id"):
            issues.append(ValidationIssue("HOLD", GateReasonCode.BLOCKED_BY_THERMODYNAMICS, f"$.diene_passports[{diene_id}].thermo_parameter_source_id", "diene thermodynamic parameters are unresolved"))
        if diene.get("terminal_model_supported") and not diene.get("kinetic_parameter_source_id"):
            issues.append(ValidationIssue("HOLD", GateReasonCode.MISSING_EVIDENCE, f"$.diene_passports[{diene_id}].kinetic_parameter_source_id", "terminal-model kinetic source is unresolved"))

    for thermo_id, thermo in thermos.items():
        for dataset_id in thermo.get("validation_dataset_ids", []):
            _require_reference(dataset_id, datasets, f"$.thermo_passports[{thermo_id}].validation_dataset_ids", "dataset", issues)
        if not thermo.get("validation_dataset_ids"):
            issues.append(ValidationIssue("HOLD", GateReasonCode.BLOCKED_BY_THERMODYNAMICS, f"$.thermo_passports[{thermo_id}].validation_dataset_ids", "thermodynamic passport has no validation dataset"))

    targets: dict[str, dict[str, Any]] = {}
    for dataset_id, dataset in datasets.items():
        _require_reference(dataset.get("catalyst_id"), catalysts, f"$.datasets[{dataset_id}].catalyst_id", "catalyst", issues)
        _require_reference(dataset.get("diene_id"), dienes, f"$.datasets[{dataset_id}].diene_id", "diene", issues)
        for target in dataset.get("targets", []):
            if isinstance(target, dict) and isinstance(target.get("target_id"), str):
                target_id = target["target_id"]
                if target_id in targets:
                    issues.append(ValidationIssue("ERROR", GateReasonCode.DATA_LEAKAGE, f"$.datasets[{dataset_id}].targets", f"duplicate target ID: {target_id}"))
                targets[target_id] = target
                if target.get("dataset_id") != dataset_id:
                    issues.append(ValidationIssue("ERROR", GateReasonCode.SEMANTIC_REFERENCE_UNRESOLVED, f"$.datasets[{dataset_id}].targets[{target_id}].dataset_id", "target dataset_id does not match parent dataset"))
    _validate_dataset_leakage(datasets, issues)
    _validate_calibration_plans(plans, all_parameters, targets, issues)

    for case_id, case in cases.items():
        _require_reference(case.get("catalyst_passport_id"), catalysts, f"$.cases[{case_id}].catalyst_passport_id", "catalyst", issues)
        _require_reference(case.get("diene_passport_id"), dienes, f"$.cases[{case_id}].diene_passport_id", "diene", issues)
        _require_reference(case.get("thermo_passport_id"), thermos, f"$.cases[{case_id}].thermo_passport_id", "thermo-passport", issues)
        _require_reference(case.get("applicability_domain_id"), domains, f"$.cases[{case_id}].applicability_domain_id", "applicability-domain", issues)
        _require_reference(case.get("kinetic_parameter_set_id"), parameter_sets, f"$.cases[{case_id}].kinetic_parameter_set_id", "kinetic-parameter-set", issues)
        state_id = case.get("state_definition_id")
        _require_reference(state_id, state_definitions, f"$.cases[{case_id}].state_definition_id", "state-definition", issues)
        state_definition = state_definitions.get(state_id)
        case_basis = case.get("initial_state", {}).get("state_basis")
        reactor_basis = case.get("reactor", {}).get("state_basis")
        definition_basis = state_definition.get("basis") if state_definition else None
        if len({case_basis, reactor_basis, definition_basis} - {None}) > 1:
            issues.append(ValidationIssue("ERROR", GateReasonCode.MIXED_STATE_BASIS, f"$.cases[{case_id}]", "case, reactor, and state definition use mixed state bases"))
        parameter_set = parameter_sets.get(case.get("kinetic_parameter_set_id"))
        if parameter_set:
            if parameter_set.get("catalyst_id") != case.get("catalyst_passport_id"):
                issues.append(ValidationIssue("ERROR", GateReasonCode.SEMANTIC_REFERENCE_UNRESOLVED, f"$.cases[{case_id}].kinetic_parameter_set_id", "parameter set catalyst does not match case catalyst"))
            if parameter_set.get("diene_id") != case.get("diene_passport_id"):
                issues.append(ValidationIssue("ERROR", GateReasonCode.UNSUPPORTED_TOPOLOGY, f"$.cases[{case_id}].kinetic_parameter_set_id", "parameter set diene does not match case diene"))
        if case.get("engineering_use_requested") is True and not case.get("qualification_report_id"):
            issues.append(ValidationIssue("ERROR", GateReasonCode.APPROVAL_MISSING, f"$.cases[{case_id}].qualification_report_id", "engineering-use request requires a qualification report"))

    qualification = project.get("qualification", {})
    if isinstance(qualification, dict):
        manual_pass = [key for key, value in qualification.items() if key.endswith("_status") and value == "PASS"]
        if manual_pass and not qualification.get("gate_results"):
            issues.append(ValidationIssue("ERROR", GateReasonCode.SEMANTIC_REFERENCE_UNRESOLVED, "$.qualification", "qualification PASS cannot be entered manually without gate results"))
        if qualification.get("engineering_use_status") == "PASS" and not qualification.get("evidence_ids"):
            issues.append(ValidationIssue("ERROR", GateReasonCode.APPROVAL_MISSING, "$.qualification.engineering_use_status", "engineering-use PASS requires approval evidence"))

    return tuple(issues)


def validate_v2_project(
    project: object,
    *,
    schema_dir: Path | None = None,
) -> V2ValidationResult:
    try:
        structural = validate_schema_instance(project, "epdm-project-v2.schema.json", schema_dir=schema_dir)
        if structural:
            return V2ValidationResult(GateDecision.FAIL, structural)
        if not isinstance(project, Mapping):
            issue = ValidationIssue("ERROR", GateReasonCode.SEMANTIC_REFERENCE_UNRESOLVED, "$", "project root must be an object")
            return V2ValidationResult(GateDecision.FAIL, (issue,))
        issues = _validate_semantics(project)
        decision = GateDecision.FAIL if any(issue.severity == "ERROR" for issue in issues) else GateDecision.HOLD if issues else GateDecision.PASS
        return V2ValidationResult(decision, issues)
    except Exception as exc:  # defensive public boundary
        issue = ValidationIssue(
            "ERROR",
            GateReasonCode.SEMANTIC_REFERENCE_UNRESOLVED,
            "$",
            f"unexpected V2 validation failure: {type(exc).__name__}",
        )
        return V2ValidationResult(GateDecision.FAIL, (issue,))
