from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

from tsao import __version__
from tsao.archive import validate_zip_archive
from tsao.doctor import diagnose
from tsao.integrity import build_release_metadata, verify_release_metadata
from tsao.provenance import build_manifest
from tsao.snapshot import build_source_snapshot

ROOT = Path(__file__).resolve().parents[1]


def test_release_metadata_detects_tampering(tmp_path: Path) -> None:
    root = tmp_path / "release"
    root.mkdir()
    (root / "data.txt").write_text("original", encoding="utf-8")
    build_release_metadata(root)
    assert verify_release_metadata(root) == []
    (root / "data.txt").write_text("tampered", encoding="utf-8")
    issues = verify_release_metadata(root)
    assert any("size mismatch" in issue or "hash mismatch" in issue for issue in issues)


def test_source_snapshot_is_deterministic_and_self_describing(tmp_path: Path) -> None:
    root = tmp_path / "source"
    (root / "reports").mkdir(parents=True)
    (root / "README.md").write_text("# demo\n", encoding="utf-8")
    build_manifest(root, root / "reports/SOURCE_CORE_MANIFEST.tsv")
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    result_one = build_source_snapshot(root, first)
    result_two = build_source_snapshot(root, second)
    assert result_one["archive_sha256"] == result_two["archive_sha256"]
    assert first.read_bytes() == second.read_bytes()
    assert validate_zip_archive(first) == []
    with zipfile.ZipFile(first) as archive:
        names = archive.namelist()
        assert any(name.endswith("SOURCE_SNAPSHOT_IDENTITY.json") for name in names)
        assert any(name.endswith("FILE_MANIFEST.tsv") for name in names)
        assert any(name.endswith("reports/SOURCE_CORE_MANIFEST.tsv") for name in names)


def test_full_doctor_verifies_distribution_metadata(tmp_path: Path) -> None:
    root = tmp_path / "copy"
    shutil.copytree(
        ROOT,
        root,
        ignore=shutil.ignore_patterns(
            ".git", "__pycache__", ".pytest_cache", ".ruff_cache", "runtime"
        ),
    )
    (root / "reports/RELEASE_IDENTITY.json").write_text(
        json.dumps(
            {
                "format": "TSAO-RELEASE-IDENTITY-1",
                "version": __version__,
                "artifact_software_qualification": "NOT_EVALUATED",
                "scientific_technical_approval": "NOT_EVALUATED",
                "engineering_design_approval": "NOT_EVALUATED",
                "industrial_performance_guarantee": "NOT_EVALUATED",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    build_manifest(root, root / "reports/SOURCE_CORE_MANIFEST.tsv")
    build_manifest(root, root / "reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv")
    build_release_metadata(root)
    result = diagnose(root, profile="full")
    assert result["pass"], result["issues"]
    (root / "README.md").write_text("changed", encoding="utf-8")
    result = diagnose(root, profile="full")
    assert not result["pass"]
    assert any(
        "provenance" in issue or "release_metadata" in issue for issue in result["issues"]
    )
