from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from . import __version__
from .archive import deterministic_zip
from .integrity import build_release_metadata, sha256_file
from .provenance import verify_manifest

_SOURCE_MANIFEST = Path("reports/SOURCE_CORE_MANIFEST.tsv")


def _manifest_paths(manifest: Path) -> list[str]:
    lines = manifest.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].split("\t")[:3] != ["path", "sha256", "bytes"]:
        raise ValueError("source manifest header mismatch")
    paths: list[str] = []
    for row_number, line in enumerate(lines[1:], start=2):
        if not line:
            continue
        fields = line.split("\t")
        if len(fields) < 3 or not fields[0]:
            raise ValueError(f"invalid source manifest row {row_number}")
        paths.append(fields[0])
    if len(paths) != len(set(paths)):
        raise ValueError("source manifest contains duplicate paths")
    return paths


def build_source_snapshot(root: Path, output: Path) -> dict[str, Any]:
    root = Path(root).resolve()
    output = Path(output).resolve(strict=False)
    manifest = root / _SOURCE_MANIFEST
    issues = verify_manifest(root, manifest)
    if issues:
        raise ValueError("source manifest verification failed: " + "; ".join(issues))
    paths = _manifest_paths(manifest)
    with tempfile.TemporaryDirectory(prefix="tsao-source-snapshot-") as directory:
        stage = Path(directory) / f"TSAO-PROCESSING-SKILL-source-{__version__}"
        stage.mkdir()
        for relative in paths:
            source = root / relative
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        manifest_target = stage / _SOURCE_MANIFEST
        manifest_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(manifest, manifest_target)
        identity = {
            "format": "TSAO-SOURCE-SNAPSHOT-1",
            "version": __version__,
            "files_from_manifest": len(paths),
            "source_manifest_sha256": sha256_file(manifest),
            "scientific_technical_approval": "NOT_EVALUATED",
            "engineering_design_approval": "NOT_EVALUATED",
            "industrial_performance_guarantee": "NOT_EVALUATED",
        }
        (stage / "SOURCE_SNAPSHOT_IDENTITY.json").write_text(
            json.dumps(identity, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        metadata = build_release_metadata(stage)
        archive_sha = deterministic_zip(stage, output)
    result = {
        **identity,
        "release_metadata_files": metadata["files"],
        "archive": str(output),
        "archive_sha256": archive_sha,
    }
    output.with_suffix(output.suffix + ".sha256").write_text(
        f"{archive_sha}  {output.name}\n", encoding="utf-8"
    )
    return result
