from __future__ import annotations

import zipfile
from pathlib import Path

from scripts.verify_wheel_contents import verify


def test_wheel_verifier_rejects_missing_skill(tmp_path: Path) -> None:
    wheel = tmp_path / "empty.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("tsao/__init__.py", "")
    result = verify(wheel)
    assert result["pass"] is False
    assert any("skills/poe" in item for item in result["errors"])


def test_wheel_verifier_rejects_controlled_binary(tmp_path: Path) -> None:
    wheel = tmp_path / "binary.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("skills/poe/historical.apw", b"binary")
    result = verify(wheel)
    assert result["pass"] is False
    assert any("controlled historical binary" in item for item in result["errors"])
