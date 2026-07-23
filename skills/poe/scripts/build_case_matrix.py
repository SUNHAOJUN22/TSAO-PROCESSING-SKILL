#!/usr/bin/env python3
"""Generate a deterministic Cartesian process-case matrix from JSON."""
from __future__ import annotations

import argparse
import csv
import itertools
import json
from collections.abc import Mapping, Sequence
from pathlib import Path


def build(spec: Mapping[str, object]) -> tuple[list[str], list[tuple[object, ...]]]:
    variables = spec.get("variables")
    if not isinstance(variables, Mapping) or not variables:
        raise ValueError("spec.variables must be a non-empty object")
    keys: list[str] = []
    levels: list[list[object]] = []
    for raw_name, raw_values in variables.items():
        name = str(raw_name).strip()
        if not name:
            raise ValueError("variable names must be non-empty")
        if not isinstance(raw_values, Sequence) or isinstance(raw_values, (str, bytes)) or not raw_values:
            raise ValueError(f"variable {name} must have a non-empty level array")
        keys.append(name)
        levels.append(list(raw_values))
    return keys, list(itertools.product(*levels))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec")
    parser.add_argument("--out", default="simulation_case_matrix.csv")
    parser.add_argument("--max-cases", type=int, default=10000)
    args = parser.parse_args(argv)
    if args.max_cases <= 0:
        parser.error("--max-cases must be positive")
    try:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        keys, rows = build(spec)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
    if len(rows) > args.max_cases:
        parser.error(f"case matrix has {len(rows)} cases; exceeds {args.max_cases}")
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["case_id", *keys])
        for index, row in enumerate(rows, start=1):
            writer.writerow([f"CASE-{index:04d}", *row])
    print(json.dumps({"cases": len(rows), "variables": keys, "out": str(output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
