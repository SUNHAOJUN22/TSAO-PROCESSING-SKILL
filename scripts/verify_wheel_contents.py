#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

_REQUIRED = {
    "skills/poe/__init__.py",
    "skills/poe/SKILL.md",
    "skills/poe/ARCHITECTURE.md",
    "skills/poe/STATUS.md",
    "skills/poe/core.py",
    "skills/poe/governance.py",
    "skills/poe/kinetics.py",
    "skills/poe/qualification.py",
    "skills/poe/package_audit.py",
    "skills/poe/estimation.py",
    "skills/poe/reactors.py",
    "skills/poe/dynamics.py",
    "skills/poe/properties.py",
    "skills/poe/scaleup.py",
    "skills/poe/model_passport.py",
    "skills/poe/data/model_asset_passports.json",
    "skills/poe/schemas/model_asset_passport.schema.json",
    "skills/poe/scripts/audit_p1.py",
    "skills/poe/data/source_asset_registry.json",
    "skills/poe/data/requirement_trace.json",
    "skills/poe/data/conflict_ledger.json",
    "skills/poe/fixtures/scientific_fixtures.json",
    "skills/poe/schemas/asset_registry.schema.json",
    "skills/poe/schemas/requirement_trace.schema.json",
    "skills/poe/schemas/conflict_ledger.schema.json",
    "skills/poe/schemas/property_method.schema.json",
    "skills/poe/schemas/process_case.schema.json",
    "skills/poe/schemas/package_manifest.schema.json",
}
_MODULES = (
    "01_product_cqa",
    "02_catalyst_impurity",
    "03_kinetics_network",
    "04_parameter_estimation",
    "05_thermodynamics_properties",
    "06_rheology_transport",
    "07_reactor_cfd_heat_removal",
    "08_steady_flowsheet_balances",
    "09_devolatilization_finishing",
    "10_recovery_recycle_purge",
    "11_dynamics_control_transitions",
    "12_scaleup_package_acceptance",
)


def _choose_wheel(wheel: Path | None, wheel_dir: Path | None) -> Path:
    if wheel is not None:
        if not wheel.is_file():
            raise ValueError(f"wheel does not exist: {wheel}")
        return wheel
    if wheel_dir is None or not wheel_dir.is_dir():
        raise ValueError("--wheel or a valid --wheel-dir is required")
    wheels = sorted(wheel_dir.glob("*.whl"))
    if len(wheels) != 1:
        raise ValueError(f"expected exactly one wheel in {wheel_dir}, found {len(wheels)}")
    return wheels[0]


def verify(wheel: Path) -> dict[str, object]:
    errors: list[str] = []
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    missing = sorted(_REQUIRED - names)
    errors.extend(f"missing wheel member: {name}" for name in missing)
    for index in range(1, 13):
        shard = f"skills/poe/data/source_asset_registry.part{index:02d}.json"
        if shard not in names:
            errors.append(f"missing wheel member: {shard}")
    for module in _MODULES:
        for filename in ("README.md", "contract.schema.json"):
            member = f"skills/poe/modules/{module}/{filename}"
            if member not in names:
                errors.append(f"missing wheel member: {member}")
    if any(name.startswith("skills/poe/tests/") for name in names):
        errors.append("wheel must not contain POE test sources")
    if any(name.endswith((".apw", ".bkp", ".dynf", ".opju", ".mat")) for name in names):
        errors.append("wheel contains controlled historical binary assets")
    return {
        "wheel": str(wheel),
        "pass": not errors,
        "errors": errors,
        "poe_members": len([name for name in names if name.startswith("skills/poe/")]),
        "module_count": len(_MODULES),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", type=Path)
    parser.add_argument("--wheel-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        result = verify(_choose_wheel(args.wheel, args.wheel_dir))
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        result = {"pass": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
