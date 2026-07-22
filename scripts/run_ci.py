from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def run(command: list[str], *, cwd: Path, timeout: int = 300) -> dict[str, Any]:
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as log:
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout,
                check=False,
            )
            returncode = result.returncode
            timed_out = False
        except subprocess.TimeoutExpired:
            returncode = 124
            timed_out = True
        log.seek(0)
        output = log.read()[-20000:]
    return {
        "command": command,
        "returncode": returncode,
        "timed_out": timed_out,
        "output": output,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    checks = [
        run(
            [sys.executable, "-m", "compileall", "-f", "-q", str(root / "tsao")],
            cwd=root,
        ),
        run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                str(root / "tests"),
            ],
            cwd=root,
        ),
        run(
            [sys.executable, "-m", "ruff", "check", "tsao", "tests", "scripts"],
            cwd=root,
        ),
    ]
    passed = all(check["returncode"] == 0 for check in checks)
    report = {
        "version": "0.1.0-alpha.2",
        "pass": passed,
        "checks": checks,
        "artifact_software_qualification": "PASS" if passed else "FAIL",
        "scientific_technical_approval": "NOT_EVALUATED",
        "engineering_design_approval": "NOT_EVALUATED",
        "customer_qualification": "NOT_EVALUATED",
        "industrial_performance_guarantee": "NOT_EVALUATED",
    }
    reports = root / "reports"
    reports.mkdir(exist_ok=True)
    target = reports / "CI_RESULTS.json"
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
