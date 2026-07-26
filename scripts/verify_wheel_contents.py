#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

_REQUIRED = {
    "tsao/process_package.py",
    "tsao/skillpacks.py",
    "tsao/data/process_package.schema.json",
    "skills/epdm/__init__.py",
    "skills/epdm/SKILL.md",
    "skills/epdm/STATUS.md",
    "skills/epdm/core.py",
    "skills/epdm/kinetics.py",
    "skills/epdm/process.py",
    "skills/epdm/qualification.py",
    "skills/epdm/package_audit.py",
    "skills/epdm/data/module_contracts.json",
    "skills/epdm/data/requirements.json",
    "skills/epdm/fixtures/reference_cases.json",
    "skills/epdm/schemas/epdm_case.schema.json",
    "skills/epdm/schemas/epdm_package.schema.json",
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
_POE_MODULES = (
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
_PROCESS_MODULES = (
    "01_chemistry_reaction_basis.md",
    "02_measurement_data.md",
    "03_thermodynamics_properties.md",
    "04_reactors_transport.md",
    "05_separation_recycle.md",
    "06_control_operability.md",
    "07_hse_reliability.md",
    "08_scaleup_pilot.md",
    "09_tea_lca_supply.md",
    "10_bioprocess.md",
    "11_electrochemical.md",
    "12_solids_crystallization.md",
    "13_fine_batch.md",
    "14_petrochemical.md",
)
_PROCESS_WORKFLOWS = (
    "00_one_shot_orchestrator.md",
    "01_evidence_and_route_selection.md",
    "02_measurement_and_experiment.md",
    "03_models_and_process_synthesis.md",
    "04_scaleup_control_hse.md",
    "05_package_acceptance_transfer.md",
)
_POLYMER_SCRIPTS = (
    "audit_evidence.py",
    "check_balance.py",
    "common.py",
    "generate_doe.py",
    "generate_master_plan.py",
    "scaleup_numbers.py",
)
_README_ASSETS = (
    "control-safety-cause-effect.svg",
    "epdm-catalyst-kinetics-network.svg",
    "epdm-identifiability-uncertainty.svg",
    "epdm-multiscale-chain.svg",
    "epdm-process-flowsheet.svg",
    "epdm-product-customer-bridge.svg",
    "epdm-reactor-mode-map.svg",
    "epdm-three-level-models.svg",
    "evidence-gate-system.svg",
    "process-package-architecture.svg",
    "process-package-data-model.svg",
    "recovery-recycle-risk-loop.svg",
    "simulation-integration-contract.svg",
    "tsao-process-intelligence-os.svg",
    "universal-process-package.svg",
    "verification-pipeline.svg",
)
_MAINTENANCE_SCRIPTS = (
    "generate_readme_assets.py",
    "generate_extended_readme_assets.py",
    "generate_decision_readme_assets.py",
    "run_ci.py",
    "verify_wheel_contents.py",
    "verify_wheel_runtime.py",
)
_SHARE_ROOT = "share/tsao-processing-skill"


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


def _has_suffix(names: set[str], suffix: str) -> bool:
    normalized = suffix.lstrip("/")
    return any(name.endswith(normalized) for name in names)


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
    for module in _POE_MODULES:
        for filename in ("README.md", "contract.schema.json"):
            member = f"skills/poe/modules/{module}/{filename}"
            if member not in names:
                errors.append(f"missing wheel member: {member}")

    share_required = {
        f"{_SHARE_ROOT}/SKILL.md",
        f"{_SHARE_ROOT}/manifest.yaml",
        f"{_SHARE_ROOT}/README.md",
        f"{_SHARE_ROOT}/README.zh-CN.md",
        f"{_SHARE_ROOT}/pyproject.toml",
        f"{_SHARE_ROOT}/docs/CAPABILITY_MATRIX.md",
        f"{_SHARE_ROOT}/reports/QUALIFICATION_BOUNDARY.md",
        f"{_SHARE_ROOT}/reports/BRANCH_CONSOLIDATION_2026-07-23.md",
        f"{_SHARE_ROOT}/reports/FINAL_AUDIT_REPORT.md",
        f"{_SHARE_ROOT}/schemas/project.schema.json",
        f"{_SHARE_ROOT}/templates/README.md",
        f"{_SHARE_ROOT}/examples/generic-process/brief.yaml",
        f"{_SHARE_ROOT}/skills/process-general/SKILL.md",
        f"{_SHARE_ROOT}/skills/process-general/manifest.yaml",
        f"{_SHARE_ROOT}/skills/epdm/SKILL.md",
        f"{_SHARE_ROOT}/skills/poe/SKILL.md",
        f"{_SHARE_ROOT}/skills/polymer-general/SKILL.md",
    }
    share_required.update(
        f"{_SHARE_ROOT}/skills/process-general/modules/{name}" for name in _PROCESS_MODULES
    )
    share_required.update(
        f"{_SHARE_ROOT}/skills/process-general/workflows/{name}"
        for name in _PROCESS_WORKFLOWS
    )
    share_required.update(
        f"{_SHARE_ROOT}/skills/polymer-general/scripts/{name}" for name in _POLYMER_SCRIPTS
    )
    share_required.update(
        f"{_SHARE_ROOT}/docs/assets/readme/{name}" for name in _README_ASSETS
    )
    share_required.update(f"{_SHARE_ROOT}/scripts/{name}" for name in _MAINTENANCE_SCRIPTS)
    errors.extend(
        f"missing installed skillpack member: {suffix}"
        for suffix in sorted(share_required)
        if not _has_suffix(names, suffix)
    )

    if any(name.startswith("skills/poe/tests/") for name in names):
        errors.append("wheel must not contain POE test sources")
    if any(name.endswith((".apw", ".bkp", ".dynf", ".opju", ".mat")) for name in names):
        errors.append("wheel contains controlled historical binary assets")
    return {
        "wheel": str(wheel),
        "pass": not errors,
        "errors": errors,
        "poe_members": len([name for name in names if name.startswith("skills/poe/")]),
        "epdm_members": len([name for name in names if name.startswith("skills/epdm/")]),
        "poe_module_count": len(_POE_MODULES),
        "process_general_module_count": len(_PROCESS_MODULES),
        "process_general_workflow_count": len(_PROCESS_WORKFLOWS),
        "readme_asset_count": len(_README_ASSETS),
        "maintenance_script_count": len(_MAINTENANCE_SCRIPTS),
        "installed_skillpack_members": len(
            [name for name in names if f"/{_SHARE_ROOT}/" in f"/{name}"]
        ),
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
