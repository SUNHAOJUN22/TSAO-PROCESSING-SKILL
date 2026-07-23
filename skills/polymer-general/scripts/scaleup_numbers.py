#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math


def positive(value: float | None, label: str) -> float | None:
    if value is None:
        return None
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise ValueError(f"{label} must be finite and positive")
    return result


def calculate(**values: float | None) -> dict[str, float | str]:
    clean = {name: positive(value, name) for name, value in values.items()}
    out: dict[str, float | str] = {}
    rho = clean.get("rho")
    mu = clean.get("mu")
    velocity = clean.get("velocity")
    length = clean.get("length")
    cp = clean.get("cp")
    conductivity = clean.get("k")
    diffusivity = clean.get("diffusivity")
    reaction_time = clean.get("reaction_time")
    mixing_time = clean.get("mixing_time")
    if None not in (rho, mu, velocity, length):
        out["Re"] = rho * velocity * length / mu  # type: ignore[operator]
    if None not in (cp, mu, conductivity):
        out["Pr"] = cp * mu / conductivity  # type: ignore[operator]
    if None not in (mu, rho, diffusivity):
        out["Sc"] = mu / (rho * diffusivity)  # type: ignore[operator]
    if None not in (reaction_time, mixing_time):
        out["Da_mixing"] = mixing_time / reaction_time  # type: ignore[operator]
    out["warning"] = (
        "Definitions and characteristic scales are process-specific; "
        "expert review is required before design use."
    )
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    for name in (
        "rho",
        "mu",
        "velocity",
        "length",
        "cp",
        "k",
        "diffusivity",
        "reaction_time",
        "mixing_time",
    ):
        parser.add_argument(f"--{name}", type=float)
    args = parser.parse_args(argv)
    try:
        out = calculate(**vars(args))
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
