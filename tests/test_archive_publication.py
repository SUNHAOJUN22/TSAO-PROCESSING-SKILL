from __future__ import annotations

import hashlib
import stat
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from tsao import archive as archive_module
from tsao.archive import deterministic_zip


def test_publication_preserves_normal_archive_creation_mode(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    (root / "data.txt").write_bytes(b"synthetic public text")
    ordinary = tmp_path / "ordinary.zip"
    with zipfile.ZipFile(ordinary, "w") as archive:
        archive.writestr("source/data.txt", b"synthetic public text")
    output = tmp_path / "published.zip"
    deterministic_zip(root, output)
    assert stat.S_IMODE(output.stat().st_mode) == stat.S_IMODE(ordinary.stat().st_mode)


def _serial_archives(tmp_path: Path) -> tuple[dict[str, Path], dict[str, str]]:
    roots: dict[str, Path] = {}
    expected: dict[str, str] = {}
    for name in ("a", "b"):
        root = tmp_path / f"source-{name}"
        root.mkdir()
        payload = f"synthetic writer {name} only\n".encode()
        (root / f"{name}.txt").write_bytes(payload)
        serial = tmp_path / f"serial-{name}.zip"
        digest = deterministic_zip(root, serial)
        assert digest == hashlib.sha256(serial.read_bytes()).hexdigest()
        with zipfile.ZipFile(serial) as archive:
            assert archive.namelist() == [f"source-{name}/{name}.txt"]
            assert archive.read(f"source-{name}/{name}.txt") == payload
        roots[name] = root
        expected[name] = digest
    return roots, expected


def test_concurrent_builds_publish_each_writers_complete_archive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    roots, expected = _serial_archives(tmp_path)
    output = tmp_path / "published" / "shared.zip"
    opened_a = threading.Event()
    opened_b = threading.Event()
    finished_a = threading.Event()
    original_writestr = zipfile.ZipFile.writestr

    def scheduled_write(archive: zipfile.ZipFile, *args, **kwargs) -> None:
        # Hold A's open file until B has opened its own staging file. Keep B
        # paused until A finishes, making shared temporary paths fail reliably.
        if threading.current_thread().name == "archive-writer-a":
            opened_a.set()
            assert opened_b.wait(10), "writer B did not open its staging file"
        else:
            opened_b.set()
            assert finished_a.wait(10), "writer A did not finish"
        original_writestr(archive, *args, **kwargs)

    def writer(name: str) -> str:
        threading.current_thread().name = f"archive-writer-{name}"
        try:
            return deterministic_zip(roots[name], output)
        finally:
            if name == "a":
                finished_a.set()

    monkeypatch.setattr(zipfile.ZipFile, "writestr", scheduled_write)
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(writer, "a")
        assert opened_a.wait(10), "writer A did not open its staging file"
        second = executor.submit(writer, "b")
        observed = {"a": first.result(timeout=15), "b": second.result(timeout=15)}

    assert observed == expected
    assert hashlib.sha256(output.read_bytes()).hexdigest() == expected["b"]
    with zipfile.ZipFile(output) as archive:
        assert archive.namelist() == ["source-b/b.txt"]
        assert archive.testzip() is None
    assert set(output.parent.iterdir()) == {output}


def test_success_digest_identifies_writer_even_if_another_writer_publishes_before_return(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    roots, expected = _serial_archives(tmp_path)
    output = tmp_path / "published" / "shared.zip"
    published_a = threading.Event()
    finished_b = threading.Event()
    original_replace = Path.replace

    def scheduled_replace(path: Path, target: Path) -> Path:
        result = original_replace(path, target)
        if target == output and threading.current_thread().name == "archive-writer-a":
            published_a.set()
            assert finished_b.wait(10), "writer B did not finish its publication"
        return result

    def writer(name: str) -> str:
        threading.current_thread().name = f"archive-writer-{name}"
        try:
            if name == "b":
                assert published_a.wait(10), "writer A did not publish its archive"
            return deterministic_zip(roots[name], output)
        finally:
            if name == "b":
                finished_b.set()

    monkeypatch.setattr(Path, "replace", scheduled_replace)
    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(writer, "a")
        second = executor.submit(writer, "b")
        observed = {"a": first.result(timeout=15), "b": second.result(timeout=15)}

    assert observed == expected
    assert hashlib.sha256(output.read_bytes()).hexdigest() == expected["b"]
    assert set(output.parent.iterdir()) == {output}


@pytest.mark.parametrize("failure_stage", ["write", "digest", "publish"])
def test_failed_build_preserves_previous_output_and_other_writers_temporary_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure_stage: str
) -> None:
    roots, _ = _serial_archives(tmp_path)
    output = tmp_path / "published" / "shared.zip"
    deterministic_zip(roots["a"], output)
    previous_bytes = output.read_bytes()
    other_temporary = output.with_name(output.name + ".tmp")
    other_temporary.write_bytes(b"another writer's unfinished archive")

    def fail(*args, **kwargs) -> None:
        raise OSError(f"synthetic {failure_stage} failure")

    if failure_stage == "write":
        monkeypatch.setattr(zipfile.ZipFile, "writestr", fail)
    elif failure_stage == "digest":
        monkeypatch.setattr(archive_module, "sha256_file", fail)
    else:
        monkeypatch.setattr(Path, "replace", fail)

    with pytest.raises(OSError, match=f"synthetic {failure_stage} failure"):
        deterministic_zip(roots["b"], output)

    assert output.read_bytes() == previous_bytes
    assert other_temporary.read_bytes() == b"another writer's unfinished archive"
    assert set(output.parent.iterdir()) == {output, other_temporary}
