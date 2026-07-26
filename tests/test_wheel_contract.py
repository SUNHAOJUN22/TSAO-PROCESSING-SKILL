from __future__ import annotations

import math
import zipfile
from pathlib import Path

from scripts.verify_wheel_contents import verify
from scripts.verify_wheel_runtime import _evaluate_payload


def test_wheel_verifier_rejects_missing_skill(tmp_path: Path) -> None:
    wheel = tmp_path / "empty.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("tsao/__init__.py", "")
    result = verify(wheel)
    assert result["pass"] is False
    assert any("skills/poe" in item for item in result["errors"])
    assert any("installed skillpack member" in item for item in result["errors"])


def test_wheel_verifier_rejects_controlled_binary(tmp_path: Path) -> None:
    wheel = tmp_path / "binary.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("skills/poe/historical.apw", b"binary")
    result = verify(wheel)
    assert result["pass"] is False
    assert any("controlled historical binary" in item for item in result["errors"])


def _valid_runtime_payload(install_root: Path) -> dict[str, object]:
    return {
        "tsao_module_path": str(install_root / "site-packages/tsao/__init__.py"),
        "epdm_module_path": str(install_root / "site-packages/skills/epdm/__init__.py"),
        "poe_module_path": str(install_root / "site-packages/skills/poe/__init__.py"),
        "pfr": 1.0 - math.exp(-1.0),
        "fit": 0.2,
        "epdm_status": "PASS",
        "package_status": "PASS",
        "skillpacks": {
            "pass": True,
            "delivery": "INSTALLED_SKILLPACK",
            "root": str(install_root / "share/tsao-processing-skill"),
            "readme_svg_assets": 16,
            "process_general_modules_present": 14,
            "process_general_workflows_present": 6,
        },
        "installed_readme_link_failures": [],
    }


def test_runtime_payload_accepts_only_install_root_members(tmp_path: Path) -> None:
    install_root = tmp_path / "installed"
    payload = _valid_runtime_payload(install_root)
    assert _evaluate_payload(payload, "TEST", expected_root=install_root) == []


def test_runtime_payload_rejects_host_editable_import(tmp_path: Path) -> None:
    install_root = tmp_path / "installed"
    payload = _valid_runtime_payload(install_root)
    payload["tsao_module_path"] = str(tmp_path / "host-checkout/tsao/__init__.py")
    errors = _evaluate_payload(payload, "TEST", expected_root=install_root)
    assert "TEST imported tsao_module_path outside the installed root" in errors


def test_runtime_payload_rejects_host_skillpack_data(tmp_path: Path) -> None:
    install_root = tmp_path / "installed"
    payload = _valid_runtime_payload(install_root)
    skillpacks = payload["skillpacks"]
    assert isinstance(skillpacks, dict)
    skillpacks["root"] = str(tmp_path / "host-checkout")
    errors = _evaluate_payload(payload, "TEST", expected_root=install_root)
    assert "TEST resolved Skillpack data outside the installed root" in errors
