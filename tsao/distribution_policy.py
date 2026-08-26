"""Fail-closed public-distribution policy for controlled POE source metadata.

The audit deliberately reports counts, classifications, and content digests only.
It never returns source asset names, original relative paths, or record payloads.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

_REGISTRY = Path("skills/poe/data/source_asset_registry.json")
_CONTROLLED_CONFIDENTIALITY = {"CONTROLLED_INTERNAL", "INTERNAL", "RESTRICTED"}
_CONTROLLED_LICENSE = {"PROJECT_CONTROLLED", "INTERNAL_ONLY", "RESTRICTED"}
_CONTROLLED_EVIDENCE = {"CONTROLLED_HISTORICAL_EVIDENCE", "CONTROLLED_EVIDENCE"}


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
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> object:
    def reject_constant(value: str) -> object:
        raise ValueError(f"non-finite JSON constant in controlled registry: {value}")

    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)


def _records(payload: object) -> list[Mapping[str, object]]:
    candidate: object = payload
    if isinstance(payload, Mapping):
        for key in ("assets", "records", "items", "entries"):
            if key in payload:
                candidate = payload[key]
                break
    if not isinstance(candidate, Sequence) or isinstance(candidate, (str, bytes, bytearray)):
        raise ValueError("registry part must contain a JSON array of records")
    result: list[Mapping[str, object]] = []
    for item in candidate:
        if not isinstance(item, Mapping):
            raise ValueError("registry part contains a non-object record")
        result.append(item)
    return result


def _safe_part_names(index: Mapping[str, object]) -> tuple[str, ...]:
    raw = index.get("asset_files")
    if not isinstance(raw, list) or not raw:
        raise ValueError("source registry index has no asset_files")
    names: list[str] = []
    for item in raw:
        if not isinstance(item, str) or not item:
            raise ValueError("source registry index contains an invalid part name")
        path = PurePosixPath(item)
        if path.is_absolute() or len(path.parts) != 1 or ".." in path.parts:
            raise ValueError("source registry index contains an unsafe part reference")
        names.append(item)
    if len(names) != len(set(names)):
        raise ValueError("source registry index contains duplicate part references")
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
        raise ValueError("controlled source registry index is missing")
    index_payload = _load_json(registry)
    if not isinstance(index_payload, Mapping):
        raise ValueError("source registry index must be a JSON object")
    part_names = _safe_part_names(index_payload)
    classification_counts: Counter[str] = Counter()
    record_count = 0
    controlled_count = 0
    part_digests: list[str] = []
    for part_name in part_names:
        part = registry.parent / part_name
        if not part.is_file():
            raise ValueError("source registry part is missing")
        part_digest = _sha256(part)
        part_digests.append(part_digest)
        for record in _records(_load_json(part)):
            record_count += 1
            classification_counts.update(_classification_labels(record))
            if _controlled(record):
                controlled_count += 1
    expected = index_payload.get("expected_asset_count", index_payload.get("asset_count"))
    if isinstance(expected, bool) or not isinstance(expected, int) or expected < 0:
        raise ValueError("source registry expected_asset_count is invalid")
    if record_count != expected:
        raise ValueError("source registry record count does not match its index")
    owner_decision_status = "PENDING_OWNER_LEGAL_IP_SECURITY_DECISION"
    status = (
        "BLOCKED_CONTROLLED_METADATA_CLASSIFICATION"
        if controlled_count > 0
        else "PASS"
    )
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
