from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

from scripts.run_ci import run


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
    for _ in range(50):
        try:
            os.kill(child_pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.05)
    else:
        pytest.fail("timed-out descendant process was not reaped")
