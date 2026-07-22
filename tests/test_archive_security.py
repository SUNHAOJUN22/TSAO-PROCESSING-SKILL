from __future__ import annotations

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


def test_archive_rejects_case_insensitive_source_collision(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    (root / "A.txt").write_text("A")
    (root / "a.txt").write_text("a")
    with pytest.raises(ValueError, match="case-insensitive"):
        deterministic_zip(root, tmp_path / "archive.zip")
