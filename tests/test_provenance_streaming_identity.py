"""Streaming identities preserve exact binary and canonical UTF-8 contracts."""

from __future__ import annotations

import hashlib
import tracemalloc
from pathlib import Path

import pytest

from tsao import provenance


@pytest.mark.parametrize("path_kind", [Path, str])
@pytest.mark.parametrize("chunk_bytes", [1, 2, 3, 7, 65536])
@pytest.mark.parametrize(
    "payload, canonical",
    [
        (b"", b""),
        (b"plain\ntext", b"plain\ntext"),
        (b"\r", b"\n"),
        (b"\r\n", b"\n"),
        (b"\r\r\n", b"\n\n"),
        ("中文 α🙂\r\n第二行\r末行".encode(), "中文 α🙂\n第二行\n末行".encode()),
        (b"\xff\r\nbinary\r", b"\xff\r\nbinary\r"),
        (b"header\r\ntext\r\xff", b"header\r\ntext\r\xff"),
        (b"header\r\ntext\r\xe4\xb8", b"header\r\ntext\r\xe4\xb8"),
    ],
)
def test_identity_is_independent_of_utf8_and_newline_chunk_boundaries(
    tmp_path, monkeypatch, path_kind, chunk_bytes, payload, canonical
):
    # The extension must not decide whether the contents are text or binary.
    path = tmp_path / "ambiguous.png"
    path.write_bytes(payload)
    monkeypatch.setattr(provenance, "_IDENTITY_CHUNK_BYTES", chunk_bytes)
    expected = hashlib.sha256(canonical).hexdigest(), len(canonical)
    assert provenance.canonical_identity(path_kind(path)) == expected
    assert provenance.canonical_bytes(path) == canonical


@pytest.mark.parametrize("path_kind", [Path, str])
@pytest.mark.parametrize("invalid_tail", [b"", b"\xff", b"\xe4\xb8"])
def test_large_text_and_late_binary_fallback_match_whole_file_contract(
    tmp_path, path_kind, invalid_tail
):
    block = provenance._IDENTITY_CHUNK_BYTES
    payload = (b"a" * (block - 1) + b"\r\n" + "中文🙂\r".encode()) * 3 + invalid_tail
    path = tmp_path / "large.dat"
    path.write_bytes(payload)
    canonical = payload if invalid_tail else payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    assert provenance.canonical_identity(path_kind(path)) == (
        hashlib.sha256(canonical).hexdigest(),
        len(canonical),
    )


def test_large_binary_has_bounded_memory_and_detects_tail_changes(tmp_path):
    payload = (b"\x89PNG\r\n\x1a\n" + bytes(range(256))) * 32_000
    path = tmp_path / "large.txt"
    path.write_bytes(payload)
    expected = hashlib.sha256(payload).hexdigest(), len(payload)
    tracemalloc.start()
    try:
        actual = provenance.canonical_identity(path)
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    assert actual == expected
    assert peak < 512 * 1024
    with path.open("r+b") as stream:
        stream.seek(-1, 2)
        stream.write(b"X")
    changed = provenance.canonical_identity(path)
    assert changed[0] != actual[0]
    assert changed[1] == actual[1]


def test_identity_reads_one_file_handle_in_bounded_chunks(tmp_path, monkeypatch):
    payload = b"\xff\r\n" + b"x" * (3 * provenance._IDENTITY_CHUNK_BYTES)
    path = tmp_path / "stream.dat"
    path.write_bytes(payload)
    original_open = provenance.os.open
    original_fdopen = provenance.os.fdopen
    opens = []
    reads = []

    class BoundedReader:
        def __init__(self, stream):
            self.stream = stream

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return self.stream.__exit__(*args)

        def read(self, size=-1):
            assert 0 < size <= provenance._IDENTITY_CHUNK_BYTES
            reads.append(size)
            return self.stream.read(size)

    def tracked_open(candidate, *args, **kwargs):
        opens.append(candidate)
        return original_open(candidate, *args, **kwargs)

    def tracked_fdopen(descriptor, *args, **kwargs):
        return BoundedReader(original_fdopen(descriptor, *args, **kwargs))

    monkeypatch.setattr(provenance.os, "open", tracked_open)
    monkeypatch.setattr(provenance.os, "fdopen", tracked_fdopen)
    assert provenance.canonical_identity(path) == (
        hashlib.sha256(payload).hexdigest(),
        len(payload),
    )
    assert opens == [path]
    assert len(reads) >= 4
