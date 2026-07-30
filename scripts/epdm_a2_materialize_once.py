from __future__ import annotations

import base64
import hashlib
import json
import lzma
import os
import re
import subprocess
import tarfile
from io import BytesIO
from pathlib import Path


def main() -> None:
    repository = os.environ["GITHUB_REPOSITORY"]
    issue_number = os.environ["ISSUE_NUMBER"]
    expected_parts = int(os.environ["EXPECTED_PARTS"])
    expected_bytes = int(os.environ["PAYLOAD_BYTES"])
    expected_digest = os.environ["PAYLOAD_SHA256"]

    raw = subprocess.check_output(
        [
            "gh",
            "api",
            f"/repos/{repository}/issues/{issue_number}/comments?per_page=100",
        ],
        text=True,
    )
    comments = json.loads(raw)
    pattern = re.compile(r"^A2_PAYLOAD_(\d{2}):([A-Za-z0-9+/=]+)$")
    parts: dict[int, str] = {}
    for comment in comments:
        for line in str(comment.get("body", "")).splitlines():
            match = pattern.fullmatch(line.strip())
            if match:
                parts[int(match.group(1))] = match.group(2)

    expected_indexes = list(range(1, expected_parts + 1))
    if sorted(parts) != expected_indexes:
        raise SystemExit(f"payload parts mismatch: {sorted(parts)}")
    compressed = base64.b64decode("".join(parts[index] for index in expected_indexes))
    if len(compressed) != expected_bytes:
        raise SystemExit(f"payload size mismatch: {len(compressed)}")
    observed = hashlib.sha256(compressed).hexdigest()
    if observed != expected_digest:
        raise SystemExit(f"payload digest mismatch: {observed}")

    archive = lzma.decompress(compressed)
    with tarfile.open(fileobj=BytesIO(archive), mode="r:") as tar:
        members = tar.getmembers()
        for member in members:
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts or not member.isfile():
                raise SystemExit(f"unsafe payload member: {member.name}")
        tar.extractall(".", members=members)

    # The first matrix proved the candidate on all six platforms. Its finalizer
    # was blocked only by a trailing blank line. Normalize the exact final tree
    # before every matrix and finalizer run so git diff --check is deterministic.
    for name in ("tests/test_wheel_contract.py",):
        path = Path(name)
        path.write_text(path.read_text(encoding="utf-8").rstrip() + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "payload_sha256": observed,
                "payload_bytes": len(compressed),
                "parts": expected_parts,
                "normalized_files": ["tests/test_wheel_contract.py"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
