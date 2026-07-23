from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tsao.doctor import diagnose

ROOT = Path(__file__).resolve().parents[1]


def test_doctor_passes_on_source_tree():
    result = diagnose(ROOT)
    assert result["pass"], result["issues"]
    assert result["version"] == "0.1.0-alpha.5"


def test_doctor_cli_is_single_entrypoint():
    result = subprocess.run([sys.executable, "-m", "tsao.cli", "doctor", "--root", str(ROOT)], text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["pass"]
