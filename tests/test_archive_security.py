from __future__ import annotations

import stat
import zipfile
from pathlib import Path

import pytest

from tsao.archive import deterministic_zip, validate_zip_archive


def test_archive_validator_rejects_backslash_drive_secret_and_member_limit(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "bad-members.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("root\\escape.txt", "bad")
        archive.writestr("C:/escape.txt", "bad")
        archive.writestr("root/private.key", "bad")
    issues = validate_zip_archive(archive_path, max_members=2)
    assert "archive member count exceeds limit" in issues
    assert any("unsafe archive path" in issue for issue in issues)
    assert "forbidden archive member: root/private.key" in issues


def test_archive_validator_rejects_case_insensitive_member_collision(tmp_path: Path) -> None:
    archive_path = tmp_path / "case-collision.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("root/A.txt", "A")
        archive.writestr("root/a.txt", "a")
    issues = validate_zip_archive(archive_path)
    assert "archive contains case-insensitive path collisions" in issues


def test_archive_rejects_case_insensitive_source_collision(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    upper = root / "A.txt"
    lower = root / "a.txt"
    upper.write_text("A")
    lower.write_text("a")
    if len(list(root.iterdir())) < 2:
        pytest.skip("filesystem is case-insensitive; source collision cannot be materialized")
    with pytest.raises(ValueError, match="case-insensitive"):
        deterministic_zip(root, tmp_path / "archive.zip")


@pytest.mark.parametrize(
    ("case", "limits", "expected"),
    [
        ("members", {"max_members": 0}, "archive member count exceeds limit"),
        ("size", {"max_uncompressed_bytes": 128}, "archive uncompressed size exceeds limit"),
        ("ratio", {"max_compression_ratio": 1}, "excessive compression ratio: root/data.txt"),
        ("unsafe", {}, "unsafe archive path: ../data.txt"),
        ("secret", {}, "forbidden archive member: root/.env"),
        ("symlink", {}, "archive contains symlink: root/data.txt"),
        ("encrypted", {}, "encrypted archive member: root/data.txt"),
    ],
)
def test_rejected_archive_metadata_prevents_content_decompression(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
    limits: dict[str, int],
    expected: str,
) -> None:
    archive_path = tmp_path / "rejected.zip"
    name = {"unsafe": "../data.txt", "secret": "root/.env"}.get(case, "root/data.txt")
    member = zipfile.ZipInfo(name)
    member.compress_type = zipfile.ZIP_DEFLATED
    if case == "symlink":
        member.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(member, b"x" * 256)
    if case == "encrypted":
        # Only the flag is needed: rejected metadata must never reach decryption.
        data = bytearray(archive_path.read_bytes())
        for signature, flag_offset in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
            offset = data.index(signature) + flag_offset
            flags = int.from_bytes(data[offset : offset + 2], "little") | 1
            data[offset : offset + 2] = flags.to_bytes(2, "little")
        archive_path.write_bytes(data)

    def reject_decompression(archive: zipfile.ZipFile) -> None:
        pytest.fail("content decompression was attempted after metadata rejection")

    monkeypatch.setattr(zipfile.ZipFile, "testzip", reject_decompression)
    assert expected in validate_zip_archive(archive_path, **limits)


@pytest.mark.parametrize("corrupt", [False, True])
def test_accepted_archive_metadata_still_requires_crc_validation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, corrupt: bool
) -> None:
    archive_path = tmp_path / "crc.zip"
    payload = b"synthetic CRC payload"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_STORED) as archive:
        archive.writestr("root/data.txt", payload)
    if corrupt:
        data = bytearray(archive_path.read_bytes())
        data[data.index(payload)] ^= 1
        archive_path.write_bytes(data)
    crc_calls = []
    original_testzip = zipfile.ZipFile.testzip

    def check_crc(archive: zipfile.ZipFile) -> str | None:
        crc_calls.append(archive.filename)
        return original_testzip(archive)

    monkeypatch.setattr(zipfile.ZipFile, "testzip", check_crc)
    issues = validate_zip_archive(archive_path)
    assert len(crc_calls) == 1
    assert issues == (["archive CRC failure: root/data.txt"] if corrupt else [])
