from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys


def run(command: list[str]) -> dict:
    result = subprocess.run(command, text=True, capture_output=True, timeout=300)
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout[-12000:],
        "stderr": result.stderr[-12000:],
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    checks = [
        run([sys.executable, "-m", "compileall", "-q", str(root / "tsao")]),
        run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(root / "tests")]),
    ]
    passed = all(check["returncode"] == 0 for check in checks)
    report = {
        "version": "0.1.0-alpha.1",
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
    (reports / "CI_RESULTS.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
