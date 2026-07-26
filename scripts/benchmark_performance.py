from __future__ import annotations

import argparse
import cProfile
import hashlib
import json
import math
import platform
import pstats
import statistics
import sys
import tempfile
import timeit
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skills.epdm.core import (  # noqa: E402
    EpdmActivationEnergies,
    EpdmKineticParameters,
    EpdmKineticState,
    SemibatchFeed,
    SemibatchInventory,
    semibatch_material_energy_step,
    three_level_kinetic_suite,
)
from skills.poe.kinetics import (  # noqa: E402
    KineticParameters,
    KineticState,
    simulate_kinetics,
)
from tsao import __version__  # noqa: E402
from tsao.process_package import validate_process_package  # noqa: E402
from tsao.provenance import build_manifest, verify_manifest  # noqa: E402

Benchmark = tuple[str, Callable[[], object], int, int]


def _json_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _profile(function: Callable[[], object], loops: int) -> list[dict[str, object]]:
    profiler = cProfile.Profile()
    profiler.enable()
    for _ in range(loops):
        function()
    profiler.disable()
    stats = pstats.Stats(profiler)
    rows: list[dict[str, object]] = []
    for (filename, line, function_name), values in sorted(
        stats.stats.items(), key=lambda item: item[1][3], reverse=True
    )[:15]:
        primitive_calls, total_calls, total_time, cumulative_time, _ = values
        rows.append(
            {
                "function": f"{Path(filename).name}:{line}:{function_name}",
                "primitive_calls": primitive_calls,
                "total_calls": total_calls,
                "total_time_s": total_time,
                "cumulative_time_s": cumulative_time,
            }
        )
    return rows


def _measure(
    name: str,
    function: Callable[[], object],
    *,
    number: int,
    repeats: int,
    profile_loops: int,
) -> dict[str, object]:
    result = function()
    samples = [value / number for value in timeit.repeat(function, number=number, repeat=repeats)]
    return {
        "name": name,
        "number_per_repeat": number,
        "repeats": repeats,
        "median_s_per_call": statistics.median(samples),
        "minimum_s_per_call": min(samples),
        "maximum_s_per_call": max(samples),
        "stdev_s_per_call": statistics.pstdev(samples),
        "result_sha256": _json_digest(result),
        "profile_loops": profile_loops,
        "profile_top_cumulative": _profile(function, profile_loops),
    }


def _epdm_suite_case() -> object:
    families = 64
    fractions = tuple(1.0 / families for _ in range(families))
    multipliers = tuple(0.55 + 0.9 * index / (families - 1) for index in range(families))
    return three_level_kinetic_suite(
        EpdmKineticState(1.2, 1.0, 0.04, 0.001, 1e-6),
        EpdmKineticParameters(2.0, 1.6, 0.5, 0.08, 0.02, 10.0),
        EpdmActivationEnergies(35_000, 37_000, 42_000, 28_000, 45_000, 20_000),
        temperature_K=323.15,
        residence_time_s=300.0,
        site_family_fractions=fractions,
        site_activity_multipliers=multipliers,
    )


def _epdm_semibatch_case() -> object:
    return semibatch_material_energy_step(
        SemibatchInventory(100.0, 120.0, 100.0, 4.0, 0.0, 323.15, 900.0),
        SemibatchFeed(0.08, 0.06, 0.002, 0.01),
        EpdmKineticParameters(2.0, 1.6, 0.5, 0.08, 0.02, 10.0),
        active_site_mol_L=0.001,
        poison_mol_L=1e-6,
        step_s=30.0,
        reaction_enthalpy_kJ_mol=85.0,
        heat_removal_kW=7.0,
    )


def _poe_rk4_case() -> object:
    return simulate_kinetics(
        KineticState(monomer_a=1.2, monomer_b=0.8, dormant_sites=0.01),
        KineticParameters(
            k_init=0.002,
            k_prop_a=0.08,
            k_prop_b=0.05,
            k_transfer=0.003,
            k_deactivation=0.0005,
        ),
        duration_s=20.0,
        step_s=0.05,
    )


def _synthetic_process_package(equipment_count: int = 500) -> dict[str, object]:
    streams: list[dict[str, object]] = []
    equipment: list[dict[str, object]] = []
    for index in range(equipment_count):
        equipment_id = f"E-{index:04d}"
        inlet = f"S-{index:04d}-IN"
        outlet = f"S-{index:04d}-OUT"
        streams.extend(
            [
                {
                    "stream_id": inlet,
                    "source": "BOUNDARY_IN",
                    "destination": equipment_id,
                    "total_mass_kg_h": 100.0,
                    "enthalpy_kW": 25.0,
                    "composition": {"A": 0.7, "B": 0.3},
                    "evidence_ids": ["EV-1"],
                },
                {
                    "stream_id": outlet,
                    "source": equipment_id,
                    "destination": "BOUNDARY_OUT",
                    "total_mass_kg_h": 100.0,
                    "enthalpy_kW": 25.0,
                    "composition": {"A": 0.7, "B": 0.3},
                    "evidence_ids": ["EV-1"],
                },
            ]
        )
        equipment.append(
            {
                "equipment_id": equipment_id,
                "inlet_stream_ids": [inlet],
                "outlet_stream_ids": [outlet],
                "duty_kW": 0.0,
                "design_status": "PASS",
            }
        )
    return {
        "package_id": "PERFORMANCE-SYNTHETIC",
        "process_family": "generic continuous process",
        "status": "NOT_EVALUATED",
        "tolerances": {"composition_abs": 1e-9, "mass_relative": 1e-9, "energy_relative": 1e-9},
        "design_basis": {
            "basis_version": "PERFORMANCE-FIXTURE",
            "capacity_kg_h": 100.0 * equipment_count,
            "operating_hours_h_y": 8_000.0,
            "components": ["A", "B"],
        },
        "streams": streams,
        "equipment": equipment,
        "utilities": [{"utility_id": "U-1", "consumption": 0.0, "unit": "kW"}],
        "controls": [
            {
                "loop_id": "LIC-1",
                "controlled_variable": "level",
                "manipulated_variable": "outlet flow",
                "measurement_tag": "LT-1",
                "final_element_tag": "LV-1",
                "status": "PASS",
            }
        ],
        "hse": [{"hazard_id": "HZ-1", "safeguards": ["independent trip"], "status": "PASS"}],
        "evidence_ledger": [
            {
                "evidence_id": "EV-1",
                "status": "QUALIFIED",
                "locator": "synthetic performance fixture",
                "applicability": "software benchmark only",
            }
        ],
        "acceptance": [
            {
                "criterion_id": "AC-1",
                "status": "PASS",
                "evidence_ids": ["EV-1"],
                "approver": "Performance Fixture",
            }
        ],
        "approvals": {
            "package_approver": "Performance Fixture",
            "process": "Performance Fixture",
            "controls": "Performance Fixture",
            "hse": "Performance Fixture",
        },
    }


def _process_package_case(package: dict[str, object]) -> object:
    return validate_process_package(package)


def _prepare_provenance_fixture(root: Path, file_count: int = 300) -> tuple[Path, Callable[[], object]]:
    for index in range(file_count):
        path = root / "sources" / f"group-{index % 10:02d}" / f"file-{index:04d}.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text((f"record={index}\n" + "0123456789abcdef" * 128), encoding="utf-8")
    target = root / "reports/SOURCE_CORE_MANIFEST.tsv"

    def exercise() -> object:
        count = build_manifest(root, target)
        issues = verify_manifest(root, target)
        return {"rows": count, "issues": issues}

    return target, exercise


def run_benchmarks(*, repeats: int) -> dict[str, object]:
    process_package = _synthetic_process_package()
    with tempfile.TemporaryDirectory(prefix="tsao-performance-") as temporary:
        _, provenance_case = _prepare_provenance_fixture(Path(temporary))
        cases: tuple[Benchmark, ...] = (
            ("epdm_three_level_64_site_families", _epdm_suite_case, 120, 20),
            ("epdm_semibatch_material_energy_step", _epdm_semibatch_case, 600, 80),
            ("poe_rk4_400_steps", _poe_rk4_case, 3, 1),
            (
                "process_package_500_equipment",
                lambda: _process_package_case(process_package),
                4,
                1,
            ),
            ("provenance_300_files_build_and_verify", provenance_case, 2, 1),
        )
        results = [
            _measure(
                name,
                function,
                number=number,
                repeats=repeats,
                profile_loops=profile_loops,
            )
            for name, function, number, profile_loops in cases
        ]
    return {
        "schema": "TSAO-PERFORMANCE-1",
        "version": __version__,
        "python": sys.version,
        "platform": platform.platform(),
        "implementation": platform.python_implementation(),
        "repeats": repeats,
        "benchmarks": results,
        "qualification_scope": "SOFTWARE_PERFORMANCE_ONLY",
        "scientific_technical_approval": "NOT_EVALUATED",
        "engineering_design_approval": "NOT_EVALUATED",
        "industrial_performance_guarantee": "NOT_EVALUATED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark TSAO computational and verification hot paths")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args(argv)
    if args.repeats < 3:
        raise ValueError("repeats must be at least 3")
    report = run_benchmarks(repeats=args.repeats)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
