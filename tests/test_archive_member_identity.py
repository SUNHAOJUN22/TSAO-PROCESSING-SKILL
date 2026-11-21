"""Real ZIP and public CLI regressions for archive member identity."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from tsao.archive import deterministic_zip, validate_zip_archive

REPO = Path(__file__).resolve().parents[1]


def _cli(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ, PYTHONPATH=str(REPO))
    return subprocess.run(
        [sys.executable, "-m", "tsao.cli", *args],
        cwd=cwd,
        env=environment,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


@pytest.mark.parametrize("source_argument", [".", "child/.."])
def test_build_cli_directory_alias_preserves_canonical_archive(
    tmp_path: Path, source_argument: str
) -> None:
    root = tmp_path / "source"
    (root / "child").mkdir(parents=True)
    (root / "data.txt").write_bytes(b"synthetic public fixture")
    reference = tmp_path / "reference.zip"
    expected_digest = deterministic_zip(root, reference)
    actual = tmp_path / "actual.zip"

    result = _cli("build", "--root", source_argument, "--out", str(actual), cwd=root)

    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["sha256"] == expected_digest
    assert actual.read_bytes() == reference.read_bytes()
    assert validate_zip_archive(actual) == []
    with zipfile.ZipFile(actual) as archive:
        assert archive.namelist() == ["source/child/", "source/data.txt"]


@pytest.mark.parametrize("location", ["root", "member"])
@pytest.mark.skipif(os.name == "nt", reason="literal backslashes are separators on Windows")
def test_builder_rejects_unsafe_source_names_before_replacing_output(
    tmp_path: Path, location: str
) -> None:
    root = tmp_path / ("unsafe\\source" if location == "root" else "source")
    root.mkdir()
    name = "unsafe\\data.txt" if location == "member" else "data.txt"
    (root / name).write_bytes(b"synthetic public fixture")
    output = tmp_path / "existing.zip"
    previous = b"previous output must remain unchanged"
    output.write_bytes(previous)

    with pytest.raises(ValueError, match="unsafe archive path"):
        deterministic_zip(root, output)

    assert output.read_bytes() == previous


@pytest.mark.parametrize(
    "name",
    ["root/./data.txt", "./root/data.txt", "root/data.txt/.", ".", "C:escape.txt"],
)
def test_validator_rejects_noncanonical_member_before_decompression(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    path = tmp_path / "noncanonical.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(name, b"synthetic public fixture")

    def reject_decompression(archive: zipfile.ZipFile) -> None:
        pytest.fail("rejected member must not reach payload decompression")

    monkeypatch.setattr(zipfile.ZipFile, "testzip", reject_decompression)
    assert f"unsafe archive path: {name}" in validate_zip_archive(path)


def test_verify_archive_cli_rejects_members_that_extract_to_the_same_file(
    tmp_path: Path,
) -> None:
    path = tmp_path / "shadowing.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("root/data.txt", b"first synthetic payload")
        archive.writestr("root/./data.txt", b"second synthetic payload")

    result = _cli("verify-archive", "--archive", str(path), cwd=REPO)

    assert result.returncode == 2, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["pass"] is False
    assert "unsafe archive path: root/./data.txt" in report["issues"]
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("corruption", ["unsupported-compression", "invalid-deflate"])
def test_verify_archive_cli_returns_structured_error_for_unreadable_payload(
    tmp_path: Path, corruption: str
) -> None:
    path = tmp_path / "unreadable.zip"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("root/data.txt", b"synthetic public fixture " * 20)
    data = bytearray(path.read_bytes())
    if corruption == "unsupported-compression":
        for signature, field_offset in ((b"PK\x03\x04", 8), (b"PK\x01\x02", 10)):
            position = data.index(signature) + field_offset
            data[position : position + 2] = (99).to_bytes(2, "little")
    else:
        header = data.index(b"PK\x03\x04")
        name_size = int.from_bytes(data[header + 26 : header + 28], "little")
        extra_size = int.from_bytes(data[header + 28 : header + 30], "little")
        # BFINAL=1, BTYPE=3 is a reserved, invalid DEFLATE block header.
        data[header + 30 + name_size + extra_size] = 0x07
    path.write_bytes(data)

    result = _cli("verify-archive", "--archive", str(path), cwd=REPO)

    assert result.returncode == 2, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["pass"] is False
    assert any(issue.startswith("invalid archive:") for issue in report["issues"])
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    "compression",
    [zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED, zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA],
)
def test_supported_archives_preserve_directory_space_and_unicode_names(
    tmp_path: Path, compression: int
) -> None:
    path = tmp_path / "valid.zip"
    with zipfile.ZipFile(path, "w", compression=compression) as archive:
        archive.writestr("root/", b"")
        archive.writestr("root/space name.txt", b"synthetic public fixture")
        archive.writestr("root/数据.txt", b"another synthetic public fixture")

    assert validate_zip_archive(path) == []
