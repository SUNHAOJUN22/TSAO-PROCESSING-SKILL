#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

REQUIRED = ("component", "in", "out", "generation", "consumption")


def number(value: object, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    if result < 0:
        raise ValueError(f"{label} must be non-negative")
    return result


def check(path: Path, tolerance: float) -> dict[str, object]:
    if tolerance < 0 or not math.isfinite(tolerance):
        raise ValueError("tolerance must be finite and non-negative")
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != REQUIRED:
            raise ValueError("balance CSV header must be: " + ",".join(REQUIRED))
        rows = list(reader)
    if not rows:
        raise ValueError("balance CSV is empty")
    components: list[dict[str, object]] = []
    total_in = total_out = total_gen = total_cons = 0.0
    seen: set[str] = set()
    for index, row in enumerate(rows, start=2):
        component = (row.get("component") or "").strip()
        if not component or component in seen:
            raise ValueError(f"row {index}: component must be non-empty and unique")
        seen.add(component)
        incoming = number(row.get("in"), f"row {index} in")
        outgoing = number(row.get("out"), f"row {index} out")
        generation = number(row.get("generation"), f"row {index} generation")
        consumption = number(row.get("consumption"), f"row {index} consumption")
        residual = incoming + generation - outgoing - consumption
        components.append({"component": component, "residual": residual})
        total_in += incoming
        total_out += outgoing
        total_gen += generation
        total_cons += consumption
    residual = total_in + total_gen - total_out - total_cons
    scale = max(abs(total_in) + abs(total_gen), abs(total_out) + abs(total_cons), 1.0)
    relative = abs(residual) / scale
    return {
        "residual": residual,
        "relative_residual": relative,
        "pass": relative <= tolerance,
        "components": components,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("--tolerance", type=float, default=1e-6)
    args = parser.parse_args(argv)
    try:
        result = check(Path(args.csv_file), args.tolerance)
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
