from __future__ import annotations

import json
from pathlib import Path

from scripts.compare_performance_v2 import compare_reports

ROOT = Path(__file__).resolve().parents[1]


def _row(name: str, time_s: float, digest: str, memory: int = 1000) -> dict[str, object]:
    return {
        "name": name,
        "median_s_per_call": time_s,
        "peak_memory_bytes": memory,
        "result_sha256": digest,
    }


def test_extended_alpha10_baseline_has_required_scale_and_memory_fields() -> None:
    report = json.loads(
        (ROOT / "reports/PERFORMANCE_BASELINE_ALPHA10_EXTENDED.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["schema"] == "TSAO-PERFORMANCE-2"
    assert report["version"] == "0.1.0-alpha.10"
    rows = {row["name"]: row for row in report["benchmarks"]}
    required = {
        "epdm_three_level_64_site_families",
        "epdm_three_level_512_site_families",
        "epdm_semibatch_10000_steps",
        "epdm_parameter_scan_1000_scalar",
        "poe_rk4_10000_steps",
        "poe_finite_difference_jacobian_8x200",
        "poe_dynamic_response_10000_points",
        "process_package_5000_equipment",
        "provenance_3000_files_build_and_verify",
        "doctor_core_repository",
        "skillpack_inventory",
        "wheel_content_verification",
    }
    assert required <= set(rows)
    for row in rows.values():
        assert row["warmups"] >= 1
        assert row["peak_memory_bytes"] > 0
        assert len(row["result_sha256"]) == 64


def test_v2_comparator_accepts_protected_and_special_paths() -> None:
    common = {
        "epdm_three_level_64_site_families": 1.0,
        "epdm_three_level_512_site_families": 8.0,
        "epdm_semibatch_material_energy_step": 1.0,
        "epdm_semibatch_10000_steps": 10.0,
        "epdm_parameter_scan_1000_scalar": 10.0,
        "poe_rk4_400_steps": 1.0,
        "poe_rk4_10000_steps": 10.0,
        "poe_finite_difference_jacobian_8x200": 1.0,
        "poe_one_parameter_fit_401_points": 1.0,
        "poe_dynamic_response_10000_points": 1.0,
        "process_package_500_equipment": 1.0,
        "process_package_5000_equipment": 10.0,
        "provenance_300_files_build_and_verify": 1.0,
        "provenance_3000_files_build_and_verify": 10.0,
        "doctor_core_repository": 1.0,
        "skillpack_inventory": 1.0,
        "wheel_content_verification": 1.0,
    }
    baseline_rows = [_row(name, value, name, memory=10_000) for name, value in common.items()]
    current_rows = [_row(name, value, name, memory=10_000) for name, value in common.items()]
    current_rows.extend(
        [
            _row("epdm_parameter_scan_1000_batch", 2.0, "batch", memory=5000),
            _row(
                "epdm_semibatch_10000_steps_compiled",
                5.0,
                "epdm_semibatch_10000_steps",
                memory=10_000,
            ),
            _row("poe_rk4_10000_steps_terminal", 5.0, "terminal", memory=2_000),
        ]
    )
    result = compare_reports(
        {"schema": "TSAO-PERFORMANCE-2", "version": "old", "benchmarks": baseline_rows},
        {
            "schema": "TSAO-PERFORMANCE-2-OPTIMIZED",
            "version": "new",
            "benchmarks": current_rows,
        },
    )
    assert result["pass"], result["errors"]
    assert len(result["scale_checks"]) == 3
    assert all(item["pass"] for item in result["optimized_path_comparisons"])


def test_v2_comparator_rejects_digest_drift() -> None:
    baseline = {
        "schema": "TSAO-PERFORMANCE-2",
        "version": "old",
        "benchmarks": [_row("epdm_three_level_64_site_families", 1.0, "old")],
    }
    current = {
        "schema": "TSAO-PERFORMANCE-2-OPTIMIZED",
        "version": "new",
        "benchmarks": [_row("epdm_three_level_64_site_families", 0.5, "new")],
    }
    result = compare_reports(baseline, current)
    assert result["pass"] is False
    assert any("digest changed" in error for error in result["errors"])
