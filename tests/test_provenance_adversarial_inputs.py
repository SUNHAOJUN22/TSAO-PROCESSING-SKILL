from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tsao import provenance
from tsao.provenance import build_manifest, verify_manifest

HEADER = "path\tsha256\tbytes\tspecialist\tartifact_class\tlicense_scope\n"


def _manifest(root: Path) -> Path:
    path = root / "reports/SOURCE_CORE_MANIFEST.tsv"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def test_manifest_builder_does_not_block_on_fifo(tmp_path: Path) -> None:
    if not hasattr(os, "mkfifo"):
        pytest.skip("named pipes are not available on this platform")
    root = tmp_path / "source"
    root.mkdir()
    (root / "source.py").write_text("VALUE = 1\n", encoding="utf-8")
    os.mkfifo(root / "stall.pipe")
    target = tmp_path / "manifest.tsv"
    command = (
        "from pathlib import Path; "
        "from tsao.provenance import build_manifest; "
        f"print(build_manifest(Path({str(root)!r}), Path({str(target)!r})))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", command],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "1"


@pytest.mark.parametrize(
    "header,row,expected_issue",
    [
        (
            HEADER,
            "source.py\t{sha}\t9\tmaster\tPUBLIC_SOURCE\n",
            "column count does not match header",
        ),
        (
            HEADER + "",
            "source.py\t{sha}\t9\tmaster\tPUBLIC_SOURCE\tPROJECT_OWNED_OR_COMPATIBLE\textra\n",
            "column count does not match header",
        ),
        (
            "path\tsha256\tbytes\tspecialist\tartifact_class\tlicense_scope\tlicense_scope\n",
            "source.py\t{sha}\t9\tmaster\tPUBLIC_SOURCE\tPROJECT_OWNED_OR_COMPATIBLE\tPROJECT_CONTROLLED\n",
            "header is invalid",
        ),
    ],
)
def test_manifest_rejects_ambiguous_or_incomplete_tsv(
    tmp_path: Path, header: str, row: str, expected_issue: str
) -> None:
    root = tmp_path
    (root / "source.py").write_text("VALUE = 1\n", encoding="utf-8")
    manifest = _manifest(root)
    manifest.write_text(
        header + row.format(sha=hashlib.sha256(b"VALUE = 1\n").hexdigest()), encoding="utf-8"
    )
    issues = verify_manifest(root, manifest)
    assert any(expected_issue in issue for issue in issues)


def test_manifest_rejects_tampered_classification_metadata(tmp_path: Path) -> None:
    root = tmp_path
    (root / "source.py").write_text("VALUE = 1\n", encoding="utf-8")
    manifest = _manifest(root)
    digest = hashlib.sha256(b"VALUE = 1\n").hexdigest()
    manifest.write_text(
        HEADER + f"source.py\t{digest}\t9\tmaster\tCONTROLLED_BINARY\tPROJECT_CONTROLLED\n",
        encoding="utf-8",
    )
    assert any(
        "classification metadata mismatch" in issue for issue in verify_manifest(root, manifest)
    )


def test_verifier_rejects_external_symlink_before_hashing_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "source"
    root.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("confidential", encoding="utf-8")
    link = root / "link.txt"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("host does not permit symlink creation")
    manifest = _manifest(root)
    digest = hashlib.sha256(b"confidential").hexdigest()
    manifest.write_text(
        HEADER + f"link.txt\t{digest}\t11\tmaster\tPUBLIC_SOURCE\tPROJECT_OWNED_OR_COMPATIBLE\n",
        encoding="utf-8",
    )

    stream_reads: list[bool] = []
    original = provenance._canonical_stream_identity

    def record_stream(source):
        stream_reads.append(True)
        return original(source)

    monkeypatch.setattr(provenance, "_canonical_stream_identity", record_stream)
    issues = verify_manifest(root, manifest)
    assert not stream_reads
    assert any("unsafe or non-regular file" in issue for issue in issues)


def test_regular_manifest_round_trip_uses_secure_relative_reader(tmp_path: Path) -> None:
    root = tmp_path / "source"
    root.mkdir()
    (root / "data.txt").write_text("alpha\r\nbeta\n", encoding="utf-8")
    manifest = _manifest(root)
    assert build_manifest(root, manifest) == 1
    assert verify_manifest(root, manifest) == []
