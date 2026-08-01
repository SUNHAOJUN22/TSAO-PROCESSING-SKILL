from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tsao.provenance import canonical_identity, classify_path  # noqa: E402

FIELDS = ["path", "sha256", "bytes", "specialist", "artifact_class", "license_scope"]


def update_overlay(root: Path, paths: list[str]) -> int:
    root = root.resolve()
    target = root / "reports/SOURCE_CORE_OVERLAY.tsv"
    records: dict[str, dict[str, object]] = {}
    if target.is_file():
        with target.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                records[str(row["path"])] = dict(row)
    for relative in paths:
        normalized = Path(relative).as_posix()
        if normalized.startswith("./"):
            normalized = normalized[2:]
        path = root / normalized
        if not path.is_file():
            raise FileNotFoundError(f"overlay path is not a file: {normalized}")
        digest, size = canonical_identity(path)
        specialist, artifact_class, license_scope = classify_path(normalized)
        records[normalized] = {
            "path": normalized,
            "sha256": digest,
            "bytes": size,
            "specialist": specialist,
            "artifact_class": artifact_class,
            "license_scope": license_scope,
        }
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(records[key] for key in sorted(records))
    return len(records)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    print(update_overlay(args.root, args.paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
