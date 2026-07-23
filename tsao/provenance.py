from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any

_EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    ".nox",
    "build",
    "dist",
    "wheelhouse",
    "htmlcov",
    "work",
}
_EXCLUDED_PREFIXES = ("reports/runtime/",)
_SELF_MANIFESTS = {
    "reports/SOURCE_CORE_MANIFEST.tsv",
    "reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv",
    "FILE_MANIFEST.tsv",
    "checksums.sha256",
    "SBOM.json",
}


def canonical_bytes(path: Path) -> bytes:
    """Return a platform-stable identity for text and exact bytes for binaries."""
    data = Path(path).read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(canonical_bytes(path)).hexdigest()


def canonical_size(path: Path) -> int:
    return len(canonical_bytes(path))


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


def _generated_part(part: str) -> bool:
    return part in _EXCLUDED_PARTS or part.endswith(".egg-info")


def iter_source_files(root: Path):
    root = Path(root)
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative_path = path.relative_to(root)
        relative = relative_path.as_posix()
        if any(_generated_part(part) for part in relative_path.parts):
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
                "bytes": canonical_size(path),
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
            lineterminator="\n",
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
            if canonical_size(path) != expected_size:
                issues.append(f"manifest row {row_number}: size mismatch {relative}")
            if sha256_file(path) != (row.get("sha256") or "").strip():
                issues.append(f"manifest row {row_number}: hash mismatch {relative}")
    if not seen:
        issues.append("source manifest contains no file records")
        return issues

    actual = {relative for _, relative in iter_source_files(root)}
    for relative in sorted(actual - seen):
        issues.append(f"unlisted source file: {relative}")
    for relative in sorted(seen - actual):
        issues.append(f"manifest lists excluded or unavailable file: {relative}")
    return issues
