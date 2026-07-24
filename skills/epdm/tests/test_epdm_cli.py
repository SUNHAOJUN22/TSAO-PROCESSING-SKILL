from __future__ import annotations

import json
import subprocess
import sys


def test_epdm_cli_reference_and_audit():
    for args in (("epdm", "status"), ("epdm", "reference-demo"), ("epdm", "audit")):
        completed = subprocess.run([sys.executable, "-m", "tsao.cli", *args], text=True, capture_output=True, check=False)
        assert completed.returncode == 0, completed.stderr
        payload = json.loads(completed.stdout)
        assert payload
