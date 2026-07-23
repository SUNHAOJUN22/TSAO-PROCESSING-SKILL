#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def family(relative: Path) -> tuple[str, str]:
    value = relative.as_posix()
    if value.startswith("skills/epdm/"):
        return "EPDM-v9", "project-controlled; validate third-party citations individually"
    if value.startswith("skills/poe/"):
        return "SJTU-POE", "project-controlled; source-corpus redistribution restrictions may apply"
    if value.startswith("skills/polymer-general/"):
        return "SJTU-universal-polymer", "project-controlled; validate embedded references individually"
    if value.startswith("vendor/"):
        return "versioned-upstream-identity", "do-not-redistribute without recorded license"
    return "TSAO-master", "Apache-2.0 unless NOTICE states otherwise"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="reports/ASSET_PROVENANCE.tsv")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    rows = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache"} for part in relative.parts):
            continue
        if path.is_symlink():
            raise SystemExit(f"symlink not permitted: {relative.as_posix()}")
        if path.is_file() and relative.as_posix() != args.out:
            asset_family, boundary = family(relative)
            rows.append({"path": relative.as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path), "asset_family": asset_family, "license_boundary": boundary})
    output = root / args.out
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"files": len(rows), "out": str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
