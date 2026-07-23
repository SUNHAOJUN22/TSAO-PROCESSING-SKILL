#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math


def _positive(value: float | None, name: str) -> float | None:
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def calculate(**values: float | None) -> dict[str, object]:
    clean = {key: _positive(value, key) for key, value in values.items()}
    output: dict[str, object] = {}
    if all(clean.get(key) is not None for key in ("rho", "mu", "velocity", "length")):
        output["Re"] = clean["rho"] * clean["velocity"] * clean["length"] / clean["mu"]
    if all(clean.get(key) is not None for key in ("cp", "mu", "k")):
        output["Pr"] = clean["cp"] * clean["mu"] / clean["k"]
    if all(clean.get(key) is not None for key in ("mu", "rho", "diffusivity")):
        output["Sc"] = clean["mu"] / (clean["rho"] * clean["diffusivity"])
    if all(clean.get(key) is not None for key in ("reaction_time", "mixing_time")):
        output["Da_mixing"] = clean["mixing_time"] / clean["reaction_time"]
    if not output:
        raise ValueError("insufficient complete variable set for any dimensionless number")
    output["warning"] = "Definitions and characteristic scales are process-specific; expert review is required before design use."
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    for name in ("rho", "mu", "velocity", "length", "cp", "k", "diffusivity", "reaction_time", "mixing_time"):
        parser.add_argument(f"--{name}", type=float)
    args = parser.parse_args(argv)
    try:
        result = calculate(**vars(args))
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
