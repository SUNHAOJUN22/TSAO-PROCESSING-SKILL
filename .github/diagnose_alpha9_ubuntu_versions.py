from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str], timeout: int = 1800) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=timeout,
    )
    output = completed.stdout or ""
    return {
        "label": label,
        "returncode": completed.returncode,
        "tail": output[-6000:] if completed.returncode else output[-1200:],
    }


def main() -> int:
    for name in (
        ".github/diagnose_alpha9_ubuntu_versions.py",
        ".github/workflows/diagnose-alpha9-ubuntu-versions-once.yml",
    ):
        (ROOT / name).unlink(missing_ok=True)

    python = sys.executable
    checks: list[dict[str, object]] = []
    commands = (
        ("generate_base_graphics", [python, "scripts/generate_readme_assets.py"]),
        ("generate_extended_graphics", [python, "scripts/generate_extended_readme_assets.py"]),
        ("generate_decision_graphics", [python, "scripts/generate_decision_readme_assets.py"]),
        ("refresh_source_manifest", [python, "-m", "tsao.cli", "doctor", "--root", ".", "--profile", "core", "--refresh-source-manifest"]),
        ("run_ci", [python, "scripts/run_ci.py"]),
        ("skillpacks", [python, "-m", "tsao.skillpacks", "--root", "."]),
        ("epdm_audit", [python, "skills/epdm/scripts/audit_epdm.py"]),
        ("poe_p0", [python, "skills/poe/scripts/audit_p0.py", "--root", "."]),
        ("poe_p1", [python, "skills/poe/scripts/audit_p1.py", "--root", "."]),
    )
    for label, command in commands:
        result = run(label, command)
        checks.append(result)
        if result["returncode"] != 0:
            break

    if all(item["returncode"] == 0 for item in checks):
        for directory in ("wheelhouse", "build", "dist"):
            shutil.rmtree(ROOT / directory, ignore_errors=True)
        for label, command in (
            ("wheel_build", [python, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation", ".", "-w", "wheelhouse"]),
            ("wheel_contents", [python, "scripts/verify_wheel_contents.py", "--wheel-dir", "wheelhouse"]),
            ("wheel_runtime", [python, "scripts/verify_wheel_runtime.py", "--wheel-dir", "wheelhouse"]),
        ):
            result = run(label, command)
            checks.append(result)
            if result["returncode"] != 0:
                break

    report = {
        "platform": sys.platform,
        "python": sys.version,
        "pass": all(item["returncode"] == 0 for item in checks),
        "checks": checks,
    }
    encoded = base64.b64encode(json.dumps(report, ensure_ascii=False).encode("utf-8")).decode("ascii")
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as stream:
            stream.write(f"report={encoded}\n")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
