"""Archive members must describe a realizable file/directory tree."""
from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from tsao.archive import deterministic_zip, validate_zip_archive


def _write_members(path: Path, names: list[str]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in names:
            archive.writestr(name, b"" if name.endswith("/") else b"synthetic payload")


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize(
    ("file_name", "descendant"),
    [
        ("root/item", "root/item/child.txt"),
        ("root/item", "root/item/"),
        ("root/ITEM", "root/item/child.txt"),
        ("root/ITEM", "root/item/"),
    ],
)
def test_file_directory_conflicts_are_rejected_before_decompression(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    file_name: str,
    descendant: str,
    reverse: bool,
) -> None:
    names = [file_name, descendant]
    if reverse:
        names.reverse()
    path = tmp_path / "conflicting.zip"
    _write_members(path, names)

    def reject_decompression(archive: zipfile.ZipFile) -> None:
        pytest.fail("file/directory conflicts must be rejected before payload decompression")

    monkeypatch.setattr(zipfile.ZipFile, "testzip", reject_decompression)
    issues = validate_zip_archive(path)
    assert f"archive file/directory path conflict: {file_name}" in issues


@pytest.mark.parametrize("reverse", [False, True])
def test_public_cli_rejects_file_as_an_implicit_parent(tmp_path: Path, reverse: bool) -> None:
    names = ["root/item", "root/item/child.txt"]
    if reverse:
        names.reverse()
    path = tmp_path / "invalid-tree.zip"
    _write_members(path, names)

    result = subprocess.run(
        [sys.executable, "-m", "tsao.cli", "verify-archive", "--archive", str(path)],
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )

    assert result.returncode == 2, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["pass"] is False
    assert "archive file/directory path conflict: root/item" in report["issues"]
    assert "Traceback" not in result.stderr


def test_builder_rejects_casefold_file_directory_conflict_without_replacing_output(
    tmp_path: Path,
) -> None:
    root = tmp_path / "source"
    directory = root / "item"
    directory.mkdir(parents=True)
    file = root / "ITEM"
    if file.exists():
        pytest.skip("case-insensitive filesystem cannot represent this source collision")
    file.write_bytes(b"file payload")
    (directory / "child.txt").write_bytes(b"child payload")
    output = tmp_path / "existing.zip"
    previous = b"previous output must remain unchanged"
    output.write_bytes(previous)

    with pytest.raises(ValueError, match="archive file/directory path conflict"):
        deterministic_zip(root, output)

    assert output.read_bytes() == previous


@pytest.mark.parametrize(
    "names",
    [
        ["root/item/child.txt", "root/item/", "root/"],
        ["root/item/child.txt", "root/other.txt"],
        ["root/item", "root/item-sibling/child.txt", "root/item.txt/child.txt"],
    ],
)
def test_realizable_explicit_implicit_and_similar_prefix_trees_remain_valid(
    tmp_path: Path, names: list[str]
) -> None:
    path = tmp_path / "valid-tree.zip"
    _write_members(path, names)

    assert validate_zip_archive(path) == []
    extracted = tmp_path / "extracted"
    with zipfile.ZipFile(path) as archive:
        archive.extractall(extracted)
    for name in names:
        target = extracted / name
        if name.endswith("/"):
            assert target.is_dir()
        else:
            assert target.read_bytes() == b"synthetic payload"
