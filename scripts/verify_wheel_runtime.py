#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path


def _choose_wheel(wheel_dir: Path) -> Path:
    wheels = sorted(wheel_dir.glob("*.whl")) if wheel_dir.is_dir() else []
    if len(wheels) != 1:
        raise ValueError(f"expected exactly one wheel in {wheel_dir}, found {len(wheels)}")
    return wheels[0]


def verify(wheel: Path) -> dict[str, object]:
    code = """
import json
from importlib.resources import files
import numpy as np
from tsao.process_package import validate_process_package
from skills.epdm.core import active_site_fraction, heat_removal_margin, validate_epdm_case
from skills.poe.core import (
    first_order_pfr_conversion,
    fit_first_order_rate,
    fopdt_response,
    validate_model_passport_registry,
)
pfr = first_order_pfr_conversion(0.2, 5.0)
times = np.linspace(0.0, 20.0, 41)
fit = fit_first_order_rate(times, 1.0 - np.exp(-0.2 * times), lower_s=0.01, upper_s=1.0)
response = fopdt_response([0.0, 1.0, 10.0], gain=1.0, time_constant_s=2.0)
passport = json.loads(files('skills.poe').joinpath('data/model_asset_passports.json').read_text(encoding='utf-8'))
validated = validate_model_passport_registry(passport)
epdm = json.loads(files('skills.epdm').joinpath('fixtures/reference_cases.json').read_text(encoding='utf-8'))
case = validate_epdm_case(epdm['valid_case'])
package = validate_process_package(epdm['valid_package'])
print(json.dumps({'pfr': pfr, 'fit': fit['rate_constant_s'], 'response': response.tolist(), 'passport_status': validated['status'], 'active_site': active_site_fraction(10,6), 'heat_margin': heat_removal_margin(80,100), 'epdm_status': case['status'], 'package_status': package['status']}))
"""
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            f"import sys; sys.path.insert(0, {str(wheel)!r});{code}",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    errors: list[str] = []
    payload: dict[str, object] = {}
    if completed.returncode != 0:
        errors.append(completed.stderr.strip() or completed.stdout.strip() or "wheel runtime failed")
    else:
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid wheel runtime output: {exc}")
        if payload and abs(float(payload.get("pfr", 0.0)) - (1.0 - math.exp(-1.0))) > 1e-12:
            errors.append("installed wheel PFR known solution mismatch")
        if payload and abs(float(payload.get("fit", 0.0)) - 0.2) > 1e-5:
            errors.append("installed wheel parameter-fit known solution mismatch")
        if payload and payload.get("epdm_status") != "PASS":
            errors.append("installed wheel EPDM reference validation failed")
        if payload and payload.get("package_status") != "PASS":
            errors.append("installed wheel universal package validation failed")
    return {"wheel": str(wheel), "pass": not errors, "errors": errors, "runtime": payload}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = verify(_choose_wheel(args.wheel_dir))
    except (OSError, ValueError) as exc:
        result = {"pass": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
