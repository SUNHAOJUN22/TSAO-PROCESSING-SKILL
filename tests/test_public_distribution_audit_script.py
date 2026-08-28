from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def test_current_controlled_registry_emits_machine_readable_block(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "audit.json"
    github_output = tmp_path / "github-output.txt"
    env = dict(os.environ)
    env["GITHUB_OUTPUT"] = str(github_output)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/write_public_distribution_audit.py",
            "--root",
            str(root),
            "--output",
            str(output),
        ],
        cwd=root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["allowed"] is False
    assert payload["status"] == "BLOCKED_CONTROLLED_METADATA_CLASSIFICATION"
    assert payload["controlled_records"] > 0
    assert payload["owner_decision"] == "PENDING_OWNER_LEGAL_IP_SECURITY_DECISION"
    workflow_values = github_output.read_text(encoding="utf-8")
    assert "allowed=false" in workflow_values
    assert "status=BLOCKED_CONTROLLED_METADATA_CLASSIFICATION" in workflow_values
    assert "BLOCKED_CONTROLLED_METADATA_CLASSIFICATION" in completed.stdout
