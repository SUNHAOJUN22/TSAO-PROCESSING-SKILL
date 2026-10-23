"""Manifest path optimizations preserve content, ordering and fail-closed checks."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import pytest

from tsao.provenance import build_manifest, canonical_identity, iter_source_files, verify_manifest


@pytest.mark.parametrize("root_style", ["absolute_path", "relative_path", "relative_text"])
def test_manifest_paths_preserve_canonical_content_and_public_iteration(
    tmp_path, monkeypatch, root_style
):
    monkeypatch.chdir(tmp_path)
    root = Path("source space 中文")
    payloads = {
        ".gitignore": (b"__pycache__/\n", b"__pycache__/\n"),
        "b.txt": (b"alpha\r\nbeta\r", b"alpha\nbeta\n"),
        "empty.txt": (b"", b""),
        "sub/data.bin": (b"raw\xff\r\n", b"raw\xff\r\n"),
        "sub/中文.md": ("中文\r\n末行".encode(), "中文\n末行".encode()),
        "sub/inside/z.txt": (b"last\n", b"last\n"),
    }
    for relative, (payload, _) in payloads.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    for relative in (".git", "sub/.git", "build/ignored.txt", "reports/runtime/ignored.json"):
        ignored = root / relative
        ignored.parent.mkdir(parents=True, exist_ok=True)
        ignored.write_bytes(b"not source identity")

    root_arg = root.absolute() if root_style == "absolute_path" else root
    if root_style == "relative_text":
        root_arg = str(root_arg)
    manifest = root / "reports/SOURCE_CORE_MANIFEST.tsv"
    assert build_manifest(root_arg, manifest) == len(payloads)
    with manifest.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    expected_paths = list(payloads)
    assert [row["path"] for row in rows] == expected_paths
    for row in rows:
        canonical = payloads[row["path"]][1]
        assert row == {
            "path": row["path"],
            "sha256": hashlib.sha256(canonical).hexdigest(),
            "bytes": str(len(canonical)),
            "specialist": "master",
            "artifact_class": "PUBLIC_SOURCE",
            "license_scope": "PROJECT_OWNED_OR_COMPATIBLE",
        }
        source = root / row["path"]
        assert canonical_identity(source) == canonical_identity(str(source))
    public_entries = list(iter_source_files(root_arg))
    assert [relative for _, relative in public_entries] == expected_paths
    assert all(isinstance(path, Path) for path, _ in public_entries)
    assert verify_manifest(root_arg, manifest) == []

    # Newline-only changes remain equivalent, while a same-size binary mutation
    # must still be detected: neither content nor stat metadata may be cached.
    (root / "b.txt").write_bytes(b"alpha\nbeta\n")
    assert verify_manifest(root_arg, manifest) == []
    (root / "sub/data.bin").write_bytes(b"raw\xfe\r\n")
    assert verify_manifest(root_arg, manifest) == ["manifest hash mismatch: sub/data.bin"]
    (root / "new.txt").write_text("new", encoding="utf-8")
    assert "unlisted source file: new.txt" in verify_manifest(root_arg, manifest)
    (root / "empty.txt").unlink()
    assert "manifest lists missing file: empty.txt" in verify_manifest(root_arg, manifest)


@pytest.mark.parametrize(
    "unsafe", ["../outside.txt", "/absolute.txt", "C:/outside.txt", "C:outside.txt", "\\\\server\\share"]
)
def test_manifest_rejects_posix_and_windows_unsafe_paths_before_file_reads(tmp_path, unsafe):
    manifest = tmp_path / "manifest.tsv"
    manifest.write_text(
        "path\tsha256\tbytes\tspecialist\tartifact_class\tlicense_scope\n"
        f"{unsafe}\t{'0' * 64}\t0\tmaster\tPUBLIC_SOURCE\tPROJECT_OWNED_OR_COMPATIBLE\n",
        encoding="utf-8",
    )
    issues = verify_manifest(tmp_path, manifest)
    assert any("unsafe manifest path" in issue for issue in issues)


@pytest.mark.parametrize("suffix", ["/", "/."])
def test_public_identity_preserves_path_normalization(tmp_path, suffix):
    source = tmp_path / "file.txt"
    source.write_bytes(b"payload")
    assert canonical_identity(str(source) + suffix) == (
        hashlib.sha256(b"payload").hexdigest(), 7
    )


@pytest.mark.parametrize("relative", ["file.txt/", "file.txt/.", "./file.txt", ".//file.txt"])
def test_noncanonical_manifest_paths_preserve_missing_vs_unlisted_diagnostics(tmp_path, relative):
    source = tmp_path / "file.txt"
    source.write_bytes(b"payload")
    manifest = tmp_path / "reports/SOURCE_CORE_MANIFEST.tsv"
    manifest.parent.mkdir()
    manifest.write_text(
        "path\tsha256\tbytes\tspecialist\tartifact_class\tlicense_scope\n"
        f"{relative}\t{hashlib.sha256(b'payload').hexdigest()}\t7\tmaster\tPUBLIC_SOURCE"
        "\tPROJECT_OWNED_OR_COMPATIBLE\n",
        encoding="utf-8",
    )
    # A noncanonical manifest key still fails completeness, but its normalized
    # target exists and has the right contents. Do not turn this into a false
    # missing-file, size or hash diagnostic during path optimization.
    assert verify_manifest(tmp_path, manifest) == [
        f"manifest lists excluded or unavailable file: {relative}",
        "unlisted source file: file.txt",
    ]
