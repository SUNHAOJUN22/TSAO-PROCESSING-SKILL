from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from scripts.run_ci import RUFF_PATHS, TEST_PATHS, run


def test_ci_runner_covers_all_specialist_suites() -> None:
    expected = {
        "tests",
        "skills/process-general/tests",
        "skills/poe/tests",
        "skills/polymer-general/tests",
    }
    assert set(TEST_PATHS) == expected
    assert expected <= set(RUFF_PATHS)


def test_ci_runner_records_success(tmp_path: Path) -> None:
    result = run([sys.executable, "-c", "print('ok')"], cwd=tmp_path, timeout=5)
    assert result["returncode"] == 0
    assert result["timed_out"] is False
    assert "ok" in result["output"]


def test_ci_runner_timeout_returns_124(tmp_path: Path) -> None:
    result = run(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        cwd=tmp_path,
        timeout=1,
    )
    assert result["returncode"] == 124
    assert result["timed_out"] is True


def _gone_or_zombie(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    if os.name == "posix":
        status = subprocess.run(
            ["ps", "-o", "stat=", "-p", str(pid)],
            text=True,
            capture_output=True,
            check=False,
        )
        return status.returncode != 0 or status.stdout.strip().startswith("Z")
    return False


@pytest.mark.skipif(os.name != "posix", reason="process-group assertion is POSIX-specific")
def test_ci_runner_timeout_kills_descendants(tmp_path: Path) -> None:
    child_pid_file = tmp_path / "child.pid"
    code = (
        "import pathlib, subprocess, sys, time; "
        "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); "
        f"pathlib.Path({str(child_pid_file)!r}).write_text(str(p.pid)); "
        "time.sleep(30)"
    )
    result = run([sys.executable, "-c", code], cwd=tmp_path, timeout=1)
    assert result["timed_out"] is True
    child_pid = int(child_pid_file.read_text())
    for _ in range(100):
        if _gone_or_zombie(child_pid):
            break
        time.sleep(0.05)
    else:
        pytest.fail("timed-out descendant process remained live")
