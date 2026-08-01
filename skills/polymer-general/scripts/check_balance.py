#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

REQUIRED = ("component", "in", "out", "generation", "consumption")


def number(value: object, label: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    if result < 0:
        raise ValueError(f"{label} must be non-negative")
    return result


def _relative_residual(
    incoming: float,
    outgoing: float,
    generation: float,
    consumption: float,
    residual: float,
) -> float:
    scale = max(incoming + generation, outgoing + consumption, 1.0)
    return abs(residual) / scale


def check(path: Path, tolerance: float) -> dict[str, object]:
    if isinstance(tolerance, bool) or tolerance < 0 or not math.isfinite(tolerance):
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
    failed_components: list[str] = []
    maximum_component_relative_residual = 0.0

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
        relative = _relative_residual(
            incoming, outgoing, generation, consumption, residual
        )
        component_pass = relative <= tolerance
        if not component_pass:
            failed_components.append(component)
        maximum_component_relative_residual = max(
            maximum_component_relative_residual, relative
        )
        components.append(
            {
                "component": component,
                "residual": residual,
                "absolute_residual": abs(residual),
                "relative_residual": relative,
                "component_pass": component_pass,
            }
        )
        total_in += incoming
        total_out += outgoing
        total_gen += generation
        total_cons += consumption

    residual = total_in + total_gen - total_out - total_cons
    relative = _relative_residual(total_in, total_out, total_gen, total_cons, residual)
    total_balance_pass = relative <= tolerance
    component_balances_pass = not failed_components
    passed = total_balance_pass and component_balances_pass
    return {
        "status": "PASS" if passed else "FAIL",
        "reason_code": "BALANCE_CLOSED" if passed else "BALANCE_NOT_CLOSED",
        "residual": residual,
        "absolute_residual": abs(residual),
        "relative_residual": relative,
        "tolerance": tolerance,
        "total_balance_pass": total_balance_pass,
        "component_balances_pass": component_balances_pass,
        "maximum_component_relative_residual": maximum_component_relative_residual,
        "failed_components": failed_components,
        "pass": passed,
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
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
