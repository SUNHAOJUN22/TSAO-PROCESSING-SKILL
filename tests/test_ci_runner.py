from __future__ import annotations

import os
import shlex
import shutil
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
        "skills/epdm/tests",
        "skills/poe/tests",
        "skills/polymer-general/tests",
    }
    assert set(TEST_PATHS) == expected
    assert {"tests", "skills/process-general", "skills/poe", "skills/polymer-general"} <= set(
        RUFF_PATHS
    )


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


def _assert_process_gone(pid: int) -> None:
    for _ in range(100):
        if _gone_or_zombie(pid):
            return
        time.sleep(0.05)
    pytest.fail(f"descendant process remained live: {pid}")


def _posix_shell() -> str:
    shell = shutil.which("sh")
    assert shell is not None, "POSIX process-group tests require sh"
    return shell


@pytest.mark.skipif(os.name != "posix", reason="process-group assertion is POSIX-specific")
def test_ci_runner_timeout_kills_descendants(tmp_path: Path) -> None:
    child_pid_file = tmp_path / "child.pid"
    target = shlex.quote(str(child_pid_file))
    code = f"sleep 30 & child=$!; printf '%s' \"$child\" > {target}; wait"
    result = run([_posix_shell(), "-c", code], cwd=tmp_path, timeout=2)
    assert result["timed_out"] is True
    assert child_pid_file.is_file(), "child PID handshake was not written before timeout"
    _assert_process_gone(int(child_pid_file.read_text()))


@pytest.mark.skipif(os.name != "posix", reason="process-group assertion is POSIX-specific")
def test_ci_runner_success_reaps_lingering_descendants(tmp_path: Path) -> None:
    child_pid_file = tmp_path / "child-success.pid"
    target = shlex.quote(str(child_pid_file))
    code = f"sleep 30 & child=$!; printf '%s' \"$child\" > {target}"
    result = run([_posix_shell(), "-c", code], cwd=tmp_path, timeout=5)
    assert result["returncode"] == 0
    assert child_pid_file.is_file(), "child PID handshake was not written"
    _assert_process_gone(int(child_pid_file.read_text()))
