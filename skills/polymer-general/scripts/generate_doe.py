#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from common import load_structured


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--factors", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--max-runs", type=int, default=256)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)
    if args.max_runs <= 0:
        parser.error("--max-runs must be positive")
    obj = load_structured(args.factors)
    factors = obj.get("factors") if isinstance(obj, dict) else obj
    if not isinstance(factors, list) or not factors:
        parser.error("factors must be a non-empty list")
    names: list[str] = []
    levels: list[list[object]] = []
    for index, factor in enumerate(factors, start=1):
        if not isinstance(factor, dict):
            parser.error(f"factor {index} must be an object")
        name = str(factor.get("name") or "").strip()
        values = factor.get("levels")
        if not name or name in names:
            parser.error("factor names must be non-empty and unique")
        if not isinstance(values, list) or len(values) < 2:
            parser.error(f"factor {name} needs at least two levels")
        names.append(name)
        levels.append(values)
    full_size = math.prod(len(value) for value in levels)
    runs = list(itertools.product(*levels))
    generator = random.Random(args.seed)
    generator.shuffle(runs)
    if len(runs) > args.max_runs:
        runs = runs[: args.max_runs]
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.writer(stream)
        writer.writerow(["run_order", *names])
        for index, row in enumerate(runs, start=1):
            writer.writerow([index, *row])
    print(
        json.dumps(
            {
                "runs": len(runs),
                "full_factorial_size": full_size,
                "seed": args.seed,
                "note": (
                    "Subsampling is not an optimized fractional factorial design; "
                    "expert review required."
                ),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
