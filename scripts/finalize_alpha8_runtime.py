from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
ISSUE = "39"
REPO = os.environ["GITHUB_REPOSITORY"]


def comment(text: str) -> None:
    subprocess.run(
        ["gh", "issue", "comment", ISSUE, "--body", text],
        check=False,
    )


def run(args: list[str], stage: str, timeout: int = 1200) -> str:
    completed = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    output = (completed.stdout + "\n" + completed.stderr).strip()
    if completed.returncode:
        comment(
            f"Alpha.8 stopped fail-closed at **{stage}**.\n\n"
            f"```text\n{output[-12000:]}\n```"
        )
        raise SystemExit(completed.returncode)
    return output


def clean() -> None:
    for name in (
        "build",
        "dist",
        "wheelhouse",
        "work",
        ".pytest_cache",
        ".ruff_cache",
    ):
        shutil.rmtree(ROOT / name, ignore_errors=True)
    for path in ROOT.rglob("__pycache__"):
        shutil.rmtree(path, ignore_errors=True)
    for path in ROOT.glob("*.egg-info"):
        shutil.rmtree(path, ignore_errors=True)
    for name in (".coverage", "coverage.xml"):
        (ROOT / name).unlink(missing_ok=True)
    for pattern in ("*.json", "*.tmp"):
        for path in (ROOT / "reports/runtime").glob(pattern):
            path.unlink(missing_ok=True)


def local_gates() -> None:
    clean()
    run(
        [
            sys.executable,
            "scripts/build_source_asset_manifest.py",
            "--root",
            ".",
            "--out",
            "reports/SOURCE_CORE_MANIFEST.tsv",
        ],
        "manifest",
    )
    run([sys.executable, "scripts/run_ci.py"], "run_ci")
    run([sys.executable, "skills/epdm/scripts/audit_epdm.py"], "EPDM audit")
    run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            ".",
            "-w",
            "wheelhouse",
        ],
        "wheel",
    )
    run(
        [
            sys.executable,
            "scripts/verify_wheel_contents.py",
            "--wheel-dir",
            "wheelhouse",
        ],
        "wheel members",
    )
    run(
        [
            sys.executable,
            "scripts/verify_wheel_runtime.py",
            "--wheel-dir",
            "wheelhouse",
        ],
        "wheel runtime",
    )


def set_status(value: str) -> None:
    path = ROOT / "reports/ALPHA8_SOURCE_CORE_STATUS.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["status"] = value
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def dispatch_and_wait(sha: str) -> int:
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    run(["gh", "workflow", "run", "ci.yml", "--ref", "main"], "dispatch CI")
    for _ in range(300):
        raw = run(
            [
                "gh",
                "api",
                f"repos/{REPO}/actions/workflows/ci.yml/runs?"
                "event=workflow_dispatch&branch=main&per_page=20",
            ],
            "query CI",
        )
        matches = [
            record
            for record in json.loads(raw).get("workflow_runs", [])
            if record.get("head_sha") == sha
            and record.get("created_at", "") >= started
        ]
        if matches:
            latest = max(matches, key=lambda record: record["created_at"])
            if latest["status"] == "completed":
                if latest.get("conclusion") != "success":
                    comment(f"Alpha.8 CI run `{latest['id']}` failed for `{sha}`.")
                    raise SystemExit(1)
                return int(latest["id"])
        time.sleep(10)
    raise SystemExit("timed out waiting for CI")


def commit_push(message: str) -> str:
    run(["git", "add", "-A"], "git add")
    run(["git", "commit", "-m", message], "git commit")
    run(["git", "push", "origin", "HEAD:main"], "git push")
    return run(["git", "rev-parse", "HEAD"], "read SHA").strip()
