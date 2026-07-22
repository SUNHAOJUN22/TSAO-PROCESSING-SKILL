from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any

_EXCLUDED_PARTS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache"}
_EXCLUDED_PREFIXES = ("reports/runtime/",)
_SELF_MANIFESTS = {
    "reports/SOURCE_CORE_MANIFEST.tsv",
    "reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv",
    "FILE_MANIFEST.tsv",
    "checksums.sha256",
    "SBOM.json",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify_path(relative: str) -> tuple[str, str, str]:
    if relative.startswith("skills/epdm/"):
        specialist = "epdm"
    elif relative.startswith("skills/poe/"):
        specialist = "poe"
    elif relative.startswith("skills/polymer-general/"):
        specialist = "polymer-general"
    elif relative.startswith("skills/process-general/"):
        specialist = "process-general"
    else:
        specialist = "master"
    if relative.endswith((".zip", ".bkp")):
        return specialist, "CONTROLLED_BINARY", "UPSTREAM_OR_FIXTURE_BINARY"
    if relative.startswith("reports/") or "/reports/" in relative:
        return specialist, "GENERATED_REPORT", "PROJECT_CONTROLLED"
    return specialist, "PUBLIC_SOURCE", "PROJECT_OWNED_OR_COMPATIBLE"


def iter_source_files(root: Path):
    root = Path(root)
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(root).as_posix()
        if any(part in _EXCLUDED_PARTS for part in path.relative_to(root).parts):
            continue
        if relative in _SELF_MANIFESTS or relative.startswith(_EXCLUDED_PREFIXES):
            continue
        yield path, relative


def build_manifest(root: Path, target: Path, *, allowed_paths: set[str] | None = None) -> int:
    root = Path(root)
    target = Path(target)
    rows: list[dict[str, Any]] = []
    for path, relative in iter_source_files(root):
        if allowed_paths is not None and relative not in allowed_paths:
            continue
        specialist, artifact_class, license_scope = classify_path(relative)
        rows.append(
            {
                "path": relative,
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
                "specialist": specialist,
                "artifact_class": artifact_class,
                "license_scope": license_scope,
            }
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "path",
                "sha256",
                "bytes",
                "specialist",
                "artifact_class",
                "license_scope",
            ],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def verify_manifest(root: Path, manifest: Path) -> list[str]:
    root = Path(root)
    manifest = Path(manifest)
    if not manifest.is_file():
        return [f"missing source manifest: {manifest}"]
    issues: list[str] = []
    seen: set[str] = set()
    with manifest.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        required = {
            "path",
            "sha256",
            "bytes",
            "specialist",
            "artifact_class",
            "license_scope",
        }
        if not required.issubset(reader.fieldnames or []):
            return ["source manifest header is incomplete"]
        for row_number, row in enumerate(reader, start=2):
            relative = (row.get("path") or "").strip()
            if not relative or relative in seen:
                issues.append(f"manifest row {row_number}: path must be non-empty and unique")
                continue
            seen.add(relative)
            path = root / relative
            if not path.is_file():
                issues.append(f"manifest row {row_number}: missing file {relative}")
                continue
            try:
                expected_size = int(row.get("bytes") or "")
            except ValueError:
                issues.append(f"manifest row {row_number}: invalid byte count")
                continue
            if path.stat().st_size != expected_size:
                issues.append(f"manifest row {row_number}: size mismatch {relative}")
            if sha256_file(path) != (row.get("sha256") or "").strip():
                issues.append(f"manifest row {row_number}: hash mismatch {relative}")
    if not seen:
        issues.append("source manifest contains no file records")
    return issues
