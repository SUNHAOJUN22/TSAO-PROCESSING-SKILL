import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, Lock

import pytest

from tsao import _utils


def test_concurrent_writers_own_distinct_temporary_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "project.json"
    rendezvous = Barrier(2)
    replace = os.replace
    paths: list[str] = []
    lock = Lock()

    def synchronized_replace(source: str, destination: str) -> None:
        with lock:
            paths.append(str(source))
        rendezvous.wait(timeout=5)
        replace(source, destination)

    monkeypatch.setattr(os, "replace", synchronized_replace)
    payloads = ['{"language":"中文"}\n', '{"language":"English"}\n']
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(_utils.atomic_write_text, target, payload) for payload in payloads]
        for future in futures:
            future.result(timeout=10)
    assert len(set(paths)) == 2
    assert target.read_text(encoding="utf-8") in payloads
    assert list(tmp_path.iterdir()) == [target]


def test_failed_publication_removes_its_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "project.json"
    target.write_text("original", encoding="utf-8")

    def fail_replace(source: str, destination: str) -> None:
        raise OSError("publication denied")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError, match="publication denied"):
        _utils.atomic_write_text(target, "replacement")
    assert target.read_text(encoding="utf-8") == "original"
    assert list(tmp_path.iterdir()) == [target]
