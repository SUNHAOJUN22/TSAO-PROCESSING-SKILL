from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tsao  # noqa: E402

__version__ = tsao.__version__

TEST_PATHS = (
    "tests",
    "skills/process-general/tests",
    "skills/epdm/tests",
    "skills/poe/tests",
    "skills/polymer-general/tests",
)
RUFF_PATHS = (
    "tsao",
    "tests",
    "scripts",
    "skills/process-general",
    "skills/epdm",
    "skills/poe",
    "skills/polymer-general",
)


def _terminate_process_tree(process: subprocess.Popen[object]) -> None:
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return
        if process.poll() is None:
            try:
                process.wait(timeout=5)
                return
            except subprocess.TimeoutExpired:
                pass
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            return
    elif os.name == "nt" and process.poll() is None:
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    elif process.poll() is None:
        process.kill()
    if process.poll() is None:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _cleanup_successful_process_group(process: subprocess.Popen[object]) -> None:
    if os.name != "posix":
        return
    try:
        os.killpg(process.pid, 0)
    except ProcessLookupError:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    time.sleep(0.05)
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def run(command: list[str], *, cwd: Path, timeout: int = 300) -> dict[str, Any]:
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as log:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            start_new_session=os.name == "posix",
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )
        try:
            returncode = process.wait(timeout=timeout)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            returncode = 124
            _terminate_process_tree(process)
        finally:
            if process.poll() is not None:
                _cleanup_successful_process_group(process)
        log.flush()
        log.seek(0)
        output = log.read()[-20000:]
    return {
        "command": command,
        "returncode": returncode,
        "timed_out": timed_out,
        "output": output,
    }


def main() -> int:
    root = ROOT
    checks = [
        run(
            [sys.executable, "-m", "compileall", "-f", "-q", "tsao", "scripts", "skills"],
            cwd=root,
        ),
        run([sys.executable, "-m", "coverage", "erase"], cwd=root),
        run(
            [
                sys.executable,
                "-m",
                "coverage",
                "run",
                "--branch",
                "--source=skills.poe,skills.epdm,tsao.process_package",
                "--omit=skills/poe/scripts/*,skills/epdm/scripts/*",
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                *TEST_PATHS,
            ],
            cwd=root,
        ),
        run(
            [sys.executable, "-m", "coverage", "report", "--fail-under=75"],
            cwd=root,
        ),
        run(
            [
                sys.executable,
                "-c",
                "from pathlib import Path; Path('.coverage').unlink(missing_ok=True); Path('coverage.xml').unlink(missing_ok=True)",
            ],
            cwd=root,
        ),
        run([sys.executable, "scripts/audit_capabilities.py"], cwd=root),
        run([sys.executable, "skills/epdm/scripts/audit_epdm.py"], cwd=root),
        run([sys.executable, "skills/poe/scripts/audit_p0.py", "--root", "."], cwd=root),
        run([sys.executable, "skills/poe/scripts/audit_p1.py", "--root", "."], cwd=root),
        run(
            [sys.executable, "-m", "tsao.cli", "doctor", "--root", ".", "--profile", "core"],
            cwd=root,
        ),
        run([sys.executable, "-m", "ruff", "check", *RUFF_PATHS], cwd=root),
    ]
    passed = all(check["returncode"] == 0 for check in checks)
    report = {
        "version": __version__,
        "pass": passed,
        "checks": checks,
        "artifact_software_qualification": "PASS" if passed else "FAIL",
        "universal_process_package_status": "EXECUTABLE_ALPHA" if passed else "HOLD",
        "epdm_software_status": "EXECUTABLE_FLAGSHIP_ALPHA_P1_REFERENCE" if passed else "HOLD",
        "poe_software_status": (
            "EXECUTABLE_SPECIALIST_ALPHA_P1_REFERENCE" if passed else "HOLD"
        ),
        "poe_scientific_execution": "UNDER_DISTILLATION",
        "scientific_technical_approval": "NOT_EVALUATED",
        "engineering_design_approval": "NOT_EVALUATED",
        "customer_qualification": "NOT_EVALUATED",
        "industrial_performance_guarantee": "NOT_EVALUATED",
    }
    target = root / "reports/runtime/CI_RESULTS.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    print(json.dumps(report, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
