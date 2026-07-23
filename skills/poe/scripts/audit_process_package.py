#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_GROUPS = (
    "design_basis",
    "pfd",
    "material_energy_balance",
    "equipment",
    "instrument_control",
    "utilities",
    "model_validation",
    "acceptance",
)


def audit(root: Path) -> dict[str, object]:
    root = Path(root)
    errors: list[str] = []
    if not root.is_dir():
        return {"root": str(root), "errors": ["package root is not a directory"], "pass": False}
    if root.is_symlink():
        errors.append("package root must not be a symlink")
    for path in root.rglob("*"):
        if path.is_symlink():
            errors.append(f"package contains symlink: {path.relative_to(root).as_posix()}")
        elif path.is_file() and path.stat().st_size == 0:
            errors.append(f"empty file: {path.relative_to(root).as_posix()}")
    for group in REQUIRED_GROUPS:
        matches = [path for path in root.rglob(f"{group}*") if path.is_file()]
        if not matches:
            errors.append(f"missing deliverable group: {group}")
    return {"root": str(root), "errors": sorted(set(errors)), "pass": not errors}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = audit(Path(args.package))
    errors = result["errors"]
    assert isinstance(errors, list)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for error in errors:
            print("ERROR", error)
        print(f"errors={len(errors)}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
