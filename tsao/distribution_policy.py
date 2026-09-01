"""Fail-closed public-distribution policy for controlled POE source metadata.

The audit deliberately reports counts, classifications, and content digests only.
It never returns source asset names, original relative paths, or record payloads.
Both package/runtime guards and the compatibility CLI import this module so the
classification semantics have one production source of truth.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

_REGISTRY = Path("skills/poe/data/source_asset_registry.json")
SCHEMA_VERSION = "tsao-processing.public-distribution-policy.v1"
BLOCKED_STATUS = "BLOCKED_CONTROLLED_METADATA_CLASSIFICATION"
_ALLOWED_SURFACES = {
    "wheel",
    "sdist",
    "source-snapshot",
    "actions-artifact",
    "release",
}
_CONTROLLED_CONFIDENTIALITY = {
    "CONTROLLED_INTERNAL",
    "INTERNAL",
    "RESTRICTED",
    "CONFIDENTIAL",
}
_CONTROLLED_LICENSE = {"PROJECT_CONTROLLED", "INTERNAL_ONLY", "RESTRICTED"}
_CONTROLLED_EVIDENCE = {"CONTROLLED_HISTORICAL_EVIDENCE", "CONTROLLED_EVIDENCE"}


class PolicyContractError(ValueError):
    """Raised when registry or decision data cannot be evaluated unambiguously."""


class DistributionBlockedError(RuntimeError):
    """Raised when a public artifact would include controlled or unclassified records."""


@dataclass(frozen=True, slots=True)
class DistributionAudit:
    status: str
    record_count: int
    controlled_record_count: int
    part_count: int
    classification_counts: dict[str, int]
    registry_sha256: str
    part_set_sha256: str
    owner_decision_status: str

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "record_count": self.record_count,
            "controlled_record_count": self.controlled_record_count,
            "part_count": self.part_count,
            "classification_counts": dict(sorted(self.classification_counts.items())),
            "registry_sha256": self.registry_sha256,
            "part_set_sha256": self.part_set_sha256,
            "owner_decision_status": self.owner_decision_status,
            "sensitive_names_or_paths_included": False,
        }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise PolicyContractError("registry artifact is missing or unreadable") from exc
    return digest.hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PolicyContractError("registry JSON contains a duplicate object key")
        result[key] = value
    return result


def _load_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda value: (_ for _ in ()).throw(
                PolicyContractError(f"non-finite JSON constant is forbidden: {value}")
            ),
        )
    except PolicyContractError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PolicyContractError("registry JSON is unreadable or invalid") from exc


def _records(payload: object) -> list[Mapping[str, object]]:
    candidate: object = payload
    if isinstance(payload, Mapping):
        for key in ("assets", "records", "items", "entries"):
            if key in payload:
                candidate = payload[key]
                break
    if not isinstance(candidate, Sequence) or isinstance(candidate, (str, bytes, bytearray)):
        raise PolicyContractError("registry part must contain a JSON array of records")
    result: list[Mapping[str, object]] = []
    for item in candidate:
        if not isinstance(item, Mapping):
            raise PolicyContractError("registry part contains a non-object record")
        result.append(item)
    return result


def _safe_part_names(index: Mapping[str, object]) -> tuple[str, ...]:
    raw = index.get("asset_files")
    if not isinstance(raw, list) or not raw:
        raise PolicyContractError("source registry index has no asset_files")
    names: list[str] = []
    for item in raw:
        if not isinstance(item, str) or not item:
            raise PolicyContractError("source registry index contains an invalid part name")
        path = PurePosixPath(item)
        if path.is_absolute() or len(path.parts) != 1 or ".." in path.parts:
            raise PolicyContractError("source registry index contains an unsafe part reference")
        names.append(item)
    if len(names) != len(set(names)):
        raise PolicyContractError("source registry index contains duplicate part references")
    return tuple(names)


def _classification_labels(record: Mapping[str, object]) -> tuple[str, ...]:
    labels: list[str] = []
    for key in ("confidentiality", "evidence_class", "license_scope"):
        value = record.get(key)
        if isinstance(value, str) and value:
            labels.append(f"{key}={value}")
    eligible = record.get("public_fixture_eligible")
    labels.append(f"public_fixture_eligible={eligible!r}")
    return tuple(labels)


def _controlled(record: Mapping[str, object]) -> bool:
    return (
        record.get("confidentiality") in _CONTROLLED_CONFIDENTIALITY
        or record.get("license_scope") in _CONTROLLED_LICENSE
        or record.get("evidence_class") in _CONTROLLED_EVIDENCE
        or record.get("public_fixture_eligible") is not True
    )


def audit_public_distribution(root: Path) -> DistributionAudit:
    root = Path(root).resolve()
    registry = root / _REGISTRY
    if not registry.is_file():
        raise PolicyContractError("controlled source registry index is missing")
    index_payload = _load_json(registry)
    if not isinstance(index_payload, Mapping):
        raise PolicyContractError("source registry index must be a JSON object")
    part_names = _safe_part_names(index_payload)
    classification_counts: Counter[str] = Counter()
    record_count = 0
    controlled_count = 0
    part_digests: list[str] = []
    for part_name in part_names:
        part = registry.parent / part_name
        if not part.is_file():
            raise PolicyContractError("source registry part is missing")
        part_digest = _sha256(part)
        part_digests.append(part_digest)
        for record in _records(_load_json(part)):
            record_count += 1
            classification_counts.update(_classification_labels(record))
            if _controlled(record):
                controlled_count += 1
    expected = index_payload.get("expected_asset_count", index_payload.get("asset_count"))
    if isinstance(expected, bool) or not isinstance(expected, int) or expected < 0:
        raise PolicyContractError("source registry expected_asset_count is invalid")
    if record_count != expected:
        raise PolicyContractError("source registry record count does not match its index")
    owner_decision_status = "PENDING_OWNER_LEGAL_IP_SECURITY_DECISION"
    status = BLOCKED_STATUS if controlled_count > 0 else "PASS"
    part_set_sha256 = hashlib.sha256("\n".join(sorted(part_digests)).encode("ascii")).hexdigest()
    return DistributionAudit(
        status=status,
        record_count=record_count,
        controlled_record_count=controlled_count,
        part_count=len(part_names),
        classification_counts=dict(classification_counts),
        registry_sha256=_sha256(registry),
        part_set_sha256=part_set_sha256,
        owner_decision_status=owner_decision_status,
    )


def assert_public_distribution_allowed(root: Path, *, artifact_kind: str) -> DistributionAudit:
    audit = audit_public_distribution(root)
    if audit.status != "PASS":
        raise DistributionBlockedError(
            f"{artifact_kind} blocked: {audit.status}; "
            f"records={audit.record_count}; controlled={audit.controlled_record_count}; "
            f"owner_decision={audit.owner_decision_status}"
        )
    return audit


def _policy_safe_part_name(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise PolicyContractError("registry part reference must be a non-empty string")
    candidate = PurePosixPath(value)
    if candidate.is_absolute() or len(candidate.parts) != 1 or ".." in candidate.parts:
        raise PolicyContractError("registry part reference is unsafe")
    if not value.startswith("source_asset_registry.part") or not value.endswith(".json"):
        raise PolicyContractError("registry part reference is outside the controlled contract")
    return value


def _policy_record_is_controlled(
    record: Mapping[str, object],
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    confidentiality = record.get("confidentiality")
    evidence_class = record.get("evidence_class")
    license_scope = record.get("license_scope")
    public_eligible = record.get("public_fixture_eligible")

    if not isinstance(confidentiality, str):
        reasons.append("MISSING_CONFIDENTIALITY")
    elif confidentiality in _CONTROLLED_CONFIDENTIALITY or any(
        token in confidentiality for token in ("CONTROLLED", "INTERNAL", "RESTRICTED")
    ):
        reasons.append("CONTROLLED_CONFIDENTIALITY")

    if not isinstance(evidence_class, str):
        reasons.append("MISSING_EVIDENCE_CLASS")
    elif "CONTROLLED" in evidence_class or "INTERNAL" in evidence_class:
        reasons.append("CONTROLLED_EVIDENCE_CLASS")

    if not isinstance(license_scope, str):
        reasons.append("MISSING_LICENSE_SCOPE")
    elif license_scope in _CONTROLLED_LICENSE or any(
        token in license_scope for token in ("CONTROLLED", "INTERNAL", "RESTRICTED")
    ):
        reasons.append("CONTROLLED_LICENSE_SCOPE")

    if public_eligible is not True:
        reasons.append("NOT_PUBLIC_FIXTURE_ELIGIBLE")

    return bool(reasons), tuple(sorted(set(reasons)))


def _decision_status(path: Path | None) -> tuple[str, str | None]:
    if path is None:
        return "PENDING_WRITTEN_DECISION", None
    payload = _load_json(path)
    if not isinstance(payload, Mapping):
        raise PolicyContractError("owner decision must be a JSON object")
    status = payload.get("status")
    if status not in {
        "PENDING_WRITTEN_DECISION",
        "DENY_PUBLIC_DISTRIBUTION",
        "RECLASSIFICATION_APPROVED_REGENERATION_REQUIRED",
    }:
        raise PolicyContractError("owner decision status is not recognized")
    digest = _sha256(path)
    if status != "PENDING_WRITTEN_DECISION":
        required = ("authorized_role", "scope", "issued_at", "artifact_sha256")
        if any(not isinstance(payload.get(field), str) or not payload[field] for field in required):
            raise PolicyContractError("owner decision is missing signed decision metadata")
        if payload["artifact_sha256"] != digest:
            raise PolicyContractError("owner decision digest does not bind its artifact")
    return str(status), digest


def evaluate_public_distribution(
    registry_root: Path,
    surfaces: Sequence[str],
    *,
    owner_decision: Path | None = None,
) -> dict[str, Any]:
    """Evaluate all requested public surfaces using the canonical registry policy."""

    root = Path(registry_root)
    manifest_path = root / "source_asset_registry.json"
    manifest = _load_json(manifest_path)
    if not isinstance(manifest, Mapping):
        raise PolicyContractError("source registry manifest must be a JSON object")
    part_values = manifest.get("asset_files")
    if not isinstance(part_values, list) or not part_values:
        raise PolicyContractError("source registry manifest has no declared parts")
    part_names = [_policy_safe_part_name(value) for value in part_values]
    if len(part_names) != len(set(part_names)):
        raise PolicyContractError("source registry manifest contains duplicate parts")

    expected_count = manifest.get("expected_asset_count")
    declared_count = manifest.get("asset_count", expected_count)
    for label, value in (
        ("expected", expected_count),
        ("declared", declared_count),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise PolicyContractError(f"{label} asset count must be a non-negative integer")

    reason_counts: Counter[str] = Counter()
    confidentiality_counts: Counter[str] = Counter()
    evidence_class_counts: Counter[str] = Counter()
    license_scope_counts: Counter[str] = Counter()
    record_count = 0
    controlled_count = 0
    public_eligible_count = 0
    asset_ids: set[str] = set()
    corpus_hasher = hashlib.sha256()
    try:
        corpus_hasher.update(manifest_path.read_bytes())
    except OSError as exc:
        raise PolicyContractError("source registry manifest is unreadable") from exc

    for part_name in part_names:
        part_path = root / part_name
        try:
            corpus_hasher.update(part_path.read_bytes())
        except OSError as exc:
            raise PolicyContractError("registry part is missing or unreadable") from exc
        payload = _load_json(part_path)
        if not isinstance(payload, Mapping) or not isinstance(payload.get("assets"), list):
            raise PolicyContractError("registry part does not contain an assets array")
        for raw_record in payload["assets"]:
            if not isinstance(raw_record, Mapping):
                raise PolicyContractError("registry asset record must be an object")
            asset_id = raw_record.get("asset_id")
            if not isinstance(asset_id, str) or not asset_id:
                raise PolicyContractError("registry asset record has no stable identifier")
            if asset_id in asset_ids:
                raise PolicyContractError("registry asset identifiers are not unique")
            asset_ids.add(asset_id)
            record_count += 1

            confidentiality = raw_record.get("confidentiality")
            evidence_class = raw_record.get("evidence_class")
            license_scope = raw_record.get("license_scope")
            confidentiality_counts[str(confidentiality or "MISSING")] += 1
            evidence_class_counts[str(evidence_class or "MISSING")] += 1
            license_scope_counts[str(license_scope or "MISSING")] += 1
            if raw_record.get("public_fixture_eligible") is True:
                public_eligible_count += 1

            controlled, reasons = _policy_record_is_controlled(raw_record)
            if controlled:
                controlled_count += 1
                reason_counts.update(reasons)

    if record_count != expected_count or record_count != declared_count:
        raise PolicyContractError("registry record count does not match the declared contract")

    normalized_surfaces = sorted(set(surfaces))
    unknown_surfaces = sorted(set(normalized_surfaces) - _ALLOWED_SURFACES)
    if unknown_surfaces:
        raise PolicyContractError("one or more distribution surfaces are not recognized")
    if not normalized_surfaces:
        raise PolicyContractError("at least one distribution surface is required")

    owner_status, owner_digest = _decision_status(owner_decision)
    blocked = controlled_count > 0
    status = BLOCKED_STATUS if blocked else "PUBLIC_DISTRIBUTION_POLICY_PASS"
    reason_codes = sorted(reason_counts)
    if blocked:
        reason_codes.append("PUBLIC_DISTRIBUTION_BLOCKED")
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "pass": not blocked,
        "privacy_minimized": True,
        "record_count": record_count,
        "controlled_record_count": controlled_count,
        "public_fixture_eligible_count": public_eligible_count,
        "distribution_surfaces": normalized_surfaces,
        "blocked_surfaces": normalized_surfaces if blocked else [],
        "owner_decision_status": owner_status,
        "owner_decision_artifact_sha256": owner_digest,
        "registry_artifact_sha256": corpus_hasher.hexdigest(),
        "classification_counts": {
            "confidentiality": dict(sorted(confidentiality_counts.items())),
            "evidence_class": dict(sorted(evidence_class_counts.items())),
            "license_scope": dict(sorted(license_scope_counts.items())),
        },
        "reason_counts": dict(sorted(reason_counts.items())),
        "reason_codes": sorted(set(reason_codes)),
        "scientific_technical_approval": "NOT_EVALUATED",
        "engineering_design_approval": "NOT_EVALUATED",
    }
    json.dumps(result, ensure_ascii=False, allow_nan=False)
    return result


def public_distribution_policy_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed public-distribution gate for parsed POE registry records."
    )
    parser.add_argument("--registry-root", type=Path, required=True)
    parser.add_argument("--surface", action="append", default=[])
    parser.add_argument("--inventory-out", type=Path, required=True)
    parser.add_argument("--owner-decision", type=Path)
    args = parser.parse_args(argv)
    try:
        result = evaluate_public_distribution(
            args.registry_root,
            list(args.surface),
            owner_decision=args.owner_decision,
        )
    except PolicyContractError as exc:
        failure = {
            "schema_version": SCHEMA_VERSION,
            "status": "INVALID_DISTRIBUTION_POLICY_INPUT",
            "pass": False,
            "privacy_minimized": True,
            "reason_codes": ["POLICY_CONTRACT_INVALID"],
            "error": str(exc),
        }
        args.inventory_out.parent.mkdir(parents=True, exist_ok=True)
        args.inventory_out.write_text(
            json.dumps(failure, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        sys.stdout.write(json.dumps(failure, ensure_ascii=False, allow_nan=False) + "\n")
        return 1

    args.inventory_out.parent.mkdir(parents=True, exist_ok=True)
    rendered = (
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    args.inventory_out.write_text(rendered, encoding="utf-8", newline="\n")
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")
    return 0 if result["pass"] else 2
