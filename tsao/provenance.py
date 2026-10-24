from __future__ import annotations

import codecs
import csv
import hashlib
import os
import stat
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, BinaryIO

_EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    ".nox",
    "build",
    "dist",
    "wheelhouse",
    "htmlcov",
    "work",
}
_EXCLUDED_PREFIXES = ("reports/runtime/",)
_EXCLUDED_FILES = {".coverage", "coverage.xml"}
_SELF_MANIFESTS = {
    "reports/SOURCE_CORE_MANIFEST.tsv",
    "reports/SOURCE_CORE_OVERLAY.tsv",
    "reports/SOURCE_ACCEPTANCE_OVERLAY.tsv",
    "reports/COMPLETE_DISTRIBUTION_MANIFEST.tsv",
    "FILE_MANIFEST.tsv",
    "checksums.sha256",
    "SBOM.json",
    "SOURCE_SNAPSHOT_IDENTITY.json",
}
_IDENTITY_CHUNK_BYTES = 64 * 1024
_MANIFEST_FIELDS = (
    "path",
    "sha256",
    "bytes",
    "specialist",
    "artifact_class",
    "license_scope",
)


def _safe_manifest_relative(value: str) -> Path:
    """Return a validated repository-relative path without filesystem access.

    The manifest format is POSIX-style on every platform.  Avoid constructing a
    ``PurePosixPath`` for each record because verification can process thousands
    of paths and this helper sits directly on that hot path.
    """
    if not value or "\\" in value or value.startswith("/"):
        raise ValueError(f"unsafe manifest path: {value}")

    # Match PurePosixPath normalization for redundant separators and ``.``
    # components while rejecting traversal and Windows-drive-like prefixes.
    parts = tuple(part for part in value.split("/") if part not in {"", "."})
    if ".." in parts or (parts and (parts[0].endswith(":") or parts[0][1:2] == ":")):
        raise ValueError(f"unsafe manifest path: {value}")
    return Path(*parts)


def _canonical_data(data: bytes) -> bytes:
    if b"\r" not in data:
        return data
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def canonical_bytes(path: Path) -> bytes:
    """Return a platform-stable identity for text and exact bytes for binaries."""
    return _canonical_data(Path(path).read_bytes())


def canonical_identity(path: Path | str) -> tuple[str, int]:
    """Return canonical SHA-256 and size in one pass with bounded read buffers.

    A late UTF-8 error makes the *entire* file binary.  Keep the raw identity
    alongside the normalized identity until UTF-8 validity is known, instead
    of rereading the file or relying on filename extensions.
    """
    # Preserve public Path normalization, including redundant trailing separators
    # and dot components, even when the caller supplies a string.
    return _canonical_path_identity(Path(path))


def _canonical_stream_identity(source: BinaryIO) -> tuple[str, int]:
    """Hash a binary stream using the canonical text/binary identity contract."""
    chunk = source.read(_IDENTITY_CHUNK_BYTES)
    if len(chunk) < _IDENTITY_CHUNK_BYTES:
        data = _canonical_data(chunk)
        return hashlib.sha256(data).hexdigest(), len(data)

    raw_digest = hashlib.sha256()
    text_digest = hashlib.sha256()
    decoder = codecs.getincrementaldecoder("utf-8")()
    raw_size = text_size = 0
    valid_utf8 = True
    previous_cr = False
    while chunk:
        raw_digest.update(chunk)
        raw_size += len(chunk)
        if valid_utf8:
            try:
                decoder.decode(chunk, final=False)
            except UnicodeDecodeError:
                valid_utf8 = False
            else:
                # CR/LF are single-byte code points in UTF-8.  A CR at the
                # previous boundary already emitted LF; consume a following
                # LF once, even when its UTF-8 chunk begins a new read.
                normalized = chunk[1:] if previous_cr and chunk.startswith(b"\n") else chunk
                previous_cr = chunk.endswith(b"\r")
                normalized = normalized.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
                text_digest.update(normalized)
                text_size += len(normalized)
        chunk = source.read(_IDENTITY_CHUNK_BYTES)
    if valid_utf8:
        try:
            decoder.decode(b"", final=True)
        except UnicodeDecodeError:
            valid_utf8 = False
    if valid_utf8:
        return text_digest.hexdigest(), text_size
    return raw_digest.hexdigest(), raw_size


def _open_regular_file(path: Path) -> BinaryIO:
    """Open a regular file without blocking on special files or following its leaf symlink."""
    flags = (
        os.O_RDONLY
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(path, flags)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError(f"source path is not a regular file: {path}")
        return os.fdopen(descriptor, "rb")
    except BaseException:
        os.close(descriptor)
        raise


@contextmanager
def _open_root_relative_file(root: Path, relative: str) -> Iterator[BinaryIO]:
    """Open a manifest path below root, rejecting symlinks at every component."""
    root = Path(root).resolve(strict=True)
    parts = _safe_manifest_relative(relative).parts
    if not parts:
        raise ValueError(f"manifest path is not a file: {relative}")

    # On POSIX, walk from an already opened root using dir_fd and O_NOFOLLOW.
    # This prevents a concurrent symlink replacement in an intermediate
    # directory from redirecting the read outside the audited tree.
    if (
        os.name == "posix"
        and os.open in os.supports_dir_fd
        and hasattr(os, "O_DIRECTORY")
        and hasattr(os, "O_NOFOLLOW")
    ):
        directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        root_fd = os.open(root, directory_flags)
        directory_fd = root_fd
        file_fd: int | None = None
        try:
            for part in parts[:-1]:
                next_fd = os.open(part, directory_flags, dir_fd=directory_fd)
                if directory_fd != root_fd:
                    os.close(directory_fd)
                directory_fd = next_fd
            file_flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
            file_fd = os.open(parts[-1], file_flags, dir_fd=directory_fd)
            if not stat.S_ISREG(os.fstat(file_fd).st_mode):
                raise ValueError(f"manifest path is not a regular file: {relative}")
            with os.fdopen(file_fd, "rb") as source:
                file_fd = None
                yield source
        finally:
            if file_fd is not None:
                os.close(file_fd)
            if directory_fd != root_fd:
                os.close(directory_fd)
            os.close(root_fd)
        return

    # Windows lacks dir_fd-relative opens. Verify each component before the
    # no-follow leaf open; this still rejects ordinary symlink manifests.
    candidate = root
    for index, part in enumerate(parts):
        candidate = candidate / part
        metadata = candidate.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise ValueError(f"manifest path traverses a symlink: {relative}")
        if index < len(parts) - 1 and not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"manifest parent is not a directory: {relative}")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise ValueError(f"manifest path escapes the audited root: {relative}")
    with _open_regular_file(candidate) as source:
        yield source


def _canonical_path_identity(path: Path) -> tuple[str, int]:
    """Hash a normalized internal regular file without reconstructing a Path per file."""
    with _open_regular_file(path) as source:
        return _canonical_stream_identity(source)


def _canonical_relative_identity(root: Path, relative: str) -> tuple[str, int]:
    with _open_root_relative_file(root, relative) as source:
        return _canonical_stream_identity(source)


def sha256_file(path: Path) -> str:
    return canonical_identity(path)[0]


def canonical_size(path: Path) -> int:
    return canonical_identity(path)[1]


def classify_path(relative: str) -> tuple[str, str, str]:
    if relative.startswith("skills/epdm/"):
        specialist = "epdm"
    elif relative.startswith("skills/poe/"):
        specialist = "poe"
    elif relative.startswith("skills/polymer-general/"):
        specialist = "polymer-general"
    elif relative.startswith("skills/process-general/"):
        specialist = "process-general"
    else:
        specialist = "master"
    if relative.endswith((".zip", ".bkp")):
        return specialist, "CONTROLLED_BINARY", "UPSTREAM_OR_FIXTURE_BINARY"
    if relative.startswith("reports/") or "/reports/" in relative:
        return specialist, "GENERATED_REPORT", "PROJECT_CONTROLLED"
    return specialist, "PUBLIC_SOURCE", "PROJECT_OWNED_OR_COMPATIBLE"


def _generated_part(part: str) -> bool:
    return part in _EXCLUDED_PARTS or part.endswith(".egg-info")


def _excluded_relative(relative: str) -> bool:
    return (
        relative in _SELF_MANIFESTS
        or relative in _EXCLUDED_FILES
        or relative.startswith(_EXCLUDED_PREFIXES)
    )


def _relative_directory(directory: str, root_string: str) -> str:
    if directory == root_string:
        return ""
    return os.path.relpath(directory, root_string).replace(os.sep, "/")


def _iter_source_paths(root: Path):
    root_path = Path(root)
    root_string = os.path.abspath(os.fspath(root_path))
    for directory, directory_names, file_names in os.walk(
        root_string, topdown=True, followlinks=False
    ):
        relative_directory = _relative_directory(directory, root_string)
        kept_directories: list[str] = []
        for name in sorted(directory_names):
            if _generated_part(name) or os.path.islink(os.path.join(directory, name)):
                continue
            relative = f"{relative_directory}/{name}/" if relative_directory else f"{name}/"
            if any(relative.startswith(prefix) for prefix in _EXCLUDED_PREFIXES):
                continue
            kept_directories.append(name)
        directory_names[:] = kept_directories
        for file_name in sorted(file_names):
            # Linked worktrees and submodules store Git metadata in a file;
            # exclude it consistently with an ordinary checkout's .git directory.
            if file_name == ".git":
                continue
            path_string = os.path.join(directory, file_name)
            try:
                mode = os.lstat(path_string).st_mode
            except OSError:
                continue
            if not stat.S_ISREG(mode):
                continue
            relative = f"{relative_directory}/{file_name}" if relative_directory else file_name
            if not _excluded_relative(relative):
                yield path_string, relative


def iter_source_files(root: Path):
    """Yield the public Path interface without imposing it on internal scans."""
    for path_string, relative in _iter_source_paths(root):
        yield Path(path_string), relative


def build_manifest(root: Path, target: Path, *, allowed_paths: set[str] | None = None) -> int:
    root = Path(root)
    target = Path(target)
    rows: list[dict[str, Any]] = []
    for _path, relative in iter_source_files(root):
        if allowed_paths is not None and relative not in allowed_paths:
            continue
        specialist, artifact_class, license_scope = classify_path(relative)
        digest, size = _canonical_relative_identity(root, relative)
        rows.append(
            {
                "path": relative,
                "sha256": digest,
                "bytes": size,
                "specialist": specialist,
                "artifact_class": artifact_class,
                "license_scope": license_scope,
            }
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=[
                "path",
                "sha256",
                "bytes",
                "specialist",
                "artifact_class",
                "license_scope",
            ],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def _read_manifest_records(
    path: Path, *, label: str
) -> tuple[dict[str, dict[str, str]], list[str]]:
    records: dict[str, dict[str, str]] = {}
    issues: list[str] = []
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        fieldnames = reader.fieldnames or []
        if (
            len(fieldnames) != len(_MANIFEST_FIELDS)
            or len(set(fieldnames)) != len(_MANIFEST_FIELDS)
            or set(fieldnames) != set(_MANIFEST_FIELDS)
        ):
            return {}, [f"{label} header is invalid"]
        for row_number, row in enumerate(reader, start=2):
            if None in row or any(row.get(key) is None for key in _MANIFEST_FIELDS):
                issues.append(f"{label} row {row_number}: column count does not match header")
                continue
            relative = (row.get("path") or "").strip()
            if not relative or relative in records:
                issues.append(f"{label} row {row_number}: path must be non-empty and unique")
                continue
            try:
                _safe_manifest_relative(relative)
                size = int(row.get("bytes") or "")
            except ValueError as exc:
                issues.append(f"{label} row {row_number}: {exc}")
                continue
            if size < 0 or not row.get("sha256") or len(row["sha256"]) != 64:
                issues.append(f"{label} row {row_number}: invalid size or SHA-256")
                continue
            if any(not (row.get(key) or "").strip() for key in _MANIFEST_FIELDS[3:]):
                issues.append(f"{label} row {row_number}: classification metadata is incomplete")
                continue
            if tuple(row[key] for key in _MANIFEST_FIELDS[3:]) != classify_path(relative):
                issues.append(f"{label} row {row_number}: classification metadata mismatch")
                continue
            records[relative] = {key: str(value or "") for key, value in row.items()}
    return records, issues


def verify_manifest(root: Path, manifest: Path) -> list[str]:
    root = Path(root)
    manifest = Path(manifest)
    if not manifest.is_file():
        return [f"missing source manifest: {manifest}"]
    records, issues = _read_manifest_records(manifest, label="manifest")
    overlay_paths = (
        root / "reports/SOURCE_CORE_OVERLAY.tsv",
        root / "reports/SOURCE_ACCEPTANCE_OVERLAY.tsv",
    )
    if manifest.name == "SOURCE_CORE_MANIFEST.tsv":
        for overlay_path in overlay_paths:
            if not overlay_path.is_file():
                continue
            overlay, overlay_issues = _read_manifest_records(overlay_path, label=overlay_path.name)
            issues.extend(overlay_issues)
            records.update(overlay)
    if not records:
        issues.append("source manifest contains no file records")
        return sorted(set(issues))

    # Every key in ``records`` already passed _safe_manifest_relative while the
    # manifest (and any overlays) were parsed. Re-validating each key here used
    # to double the path-normalization work in large-manifest verification.
    for relative, row in records.items():
        # Reuse this normalized Path, including its cached filesystem string,
        # for both the metadata check and the single content read below.
        expected_size = int(row["bytes"])
        try:
            digest, size = _canonical_relative_identity(root, relative)
        except (FileNotFoundError, NotADirectoryError):
            issues.append(f"manifest lists missing file: {relative}")
            continue
        except (OSError, ValueError) as exc:
            issues.append(f"manifest lists unsafe or non-regular file: {relative}: {exc}")
            continue
        if size != expected_size:
            issues.append(f"manifest size mismatch: {relative}")
        if digest != row["sha256"].strip():
            issues.append(f"manifest hash mismatch: {relative}")

    actual = {relative for _, relative in _iter_source_paths(root)}
    seen = set(records)
    for relative in sorted(actual - seen):
        issues.append(f"unlisted source file: {relative}")
    for relative in sorted(seen - actual):
        issues.append(f"manifest lists excluded or unavailable file: {relative}")
    return sorted(set(issues))
