from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tsao.skillpacks import resolve_skillpack_root, skillpack_inventory

ROOT = Path(__file__).resolve().parents[1]


def test_source_checkout_skillpack_inventory_is_complete():
    inventory = skillpack_inventory(ROOT)
    assert inventory["pass"] is True
    assert inventory["delivery"] == "SOURCE_CHECKOUT"
    assert inventory["subskills"] == ["epdm", "poe", "polymer-general", "process-general"]
    assert inventory["process_general_modules"] == 14
    assert inventory["process_general_workflows"] == 6
    assert inventory["polymer_general_scripts"] == 6
    assert inventory["readme_svg_assets"] >= 12
    assert inventory["scientific_technical_approval"] == "NOT_EVALUATED"


def test_skillpack_root_rejects_incomplete_directory(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        resolve_skillpack_root(tmp_path)


def test_skillpacks_module_reports_source_delivery():
    completed = subprocess.run(
        [sys.executable, "-m", "tsao.skillpacks", "--root", str(ROOT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["pass"] is True
    assert payload["delivery"] == "SOURCE_CHECKOUT"
