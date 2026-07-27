from __future__ import annotations

import argparse
import json
from pathlib import Path

COMMON_MINIMUM_RATIO = {
    "epdm_three_level_64_site_families": 0.90,
    "epdm_three_level_512_site_families": 0.90,
    "epdm_semibatch_material_energy_step": 0.90,
    "epdm_semibatch_10000_steps": 0.90,
    "epdm_parameter_scan_1000_scalar": 0.90,
    "poe_rk4_400_steps": 0.90,
    "poe_rk4_10000_steps": 0.90,
    "poe_finite_difference_jacobian_8x200": 0.90,
    "poe_one_parameter_fit_401_points": 0.90,
    "poe_dynamic_response_10000_points": 0.90,
    "process_package_500_equipment": 0.85,
    "process_package_5000_equipment": 0.85,
    "provenance_300_files_build_and_verify": 0.90,
    "provenance_3000_files_build_and_verify": 0.90,
    "doctor_core_repository": 0.85,
    "skillpack_inventory": 0.85,
    "wheel_content_verification": 0.85,
}


def _load(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not str(data.get("schema", "")).startswith(
        "TSAO-PERFORMANCE-2"
    ):
        raise ValueError(f"invalid v2 performance report: {path}")
    return data


def _rows(report: dict[str, object]) -> dict[str, dict[str, object]]:
    return {
        str(row["name"]): row
        for row in report.get("benchmarks", [])
        if isinstance(row, dict) and "name" in row
    }


def _time(row: dict[str, object]) -> float:
    return float(row["median_s_per_call"])


def _memory(row: dict[str, object]) -> int:
    return int(row["peak_memory_bytes"])


def _scale_check(
    rows: dict[str, dict[str, object]],
    *,
    small: str,
    large: str,
    size_ratio: float,
    limit: float,
) -> dict[str, object]:
    missing = [name for name in (small, large) if name not in rows]
    if missing:
        return {
            "small": small,
            "large": large,
            "size_ratio": size_ratio,
            "normalized_time_ratio": None,
            "maximum_normalized_time_ratio": limit,
            "missing_workloads": missing,
            "pass": False,
        }
    normalized_ratio = (_time(rows[large]) / _time(rows[small])) / size_ratio
    return {
        "small": small,
        "large": large,
        "size_ratio": size_ratio,
        "normalized_time_ratio": normalized_ratio,
        "maximum_normalized_time_ratio": limit,
        "missing_workloads": [],
        "pass": normalized_ratio <= limit,
    }


def compare_reports(
    baseline: dict[str, object], current: dict[str, object]
) -> dict[str, object]:
    baseline_rows = _rows(baseline)
    current_rows = _rows(current)
    errors: list[str] = []
    comparisons: list[dict[str, object]] = []

    missing = sorted(set(baseline_rows) - set(current_rows))
    if missing:
        errors.append(f"current report is missing baseline workloads: {missing}")
    for name, before in sorted(baseline_rows.items()):
        after = current_rows.get(name)
        if after is None:
            continue
        ratio = _time(before) / _time(after) if _time(after) > 0 else float("inf")
        minimum = COMMON_MINIMUM_RATIO.get(name, 0.85)
        result_match = before.get("result_sha256") == after.get("result_sha256")
        passed = result_match and ratio >= minimum
        if not result_match:
            errors.append(f"{name}: numerical result digest changed")
        if ratio < minimum:
            errors.append(
                f"{name}: performance ratio {ratio:.3f}x is below {minimum:.3f}x"
            )
        comparisons.append(
            {
                "name": name,
                "baseline_median_s": _time(before),
                "optimized_median_s": _time(after),
                "performance_ratio": ratio,
                "minimum_ratio": minimum,
                "baseline_peak_memory_bytes": _memory(before),
                "optimized_peak_memory_bytes": _memory(after),
                "result_digest_match": result_match,
                "pass": passed,
            }
        )

    special_specs = (
        (
            "epdm_parameter_scan_1000_batch",
            "epdm_parameter_scan_1000_scalar",
            3.0,
            None,
            "scalar-vs-batch tolerance contract",
        ),
        (
            "epdm_semibatch_10000_steps_compiled",
            "epdm_semibatch_10000_steps",
            1.5,
            1.0,
            "exact structured digest",
        ),
        (
            "poe_rk4_10000_steps_terminal",
            "poe_rk4_10000_steps",
            1.5,
            0.25,
            "terminal/full final-state and metrics contract",
        ),
    )
    special: list[dict[str, object]] = []
    for current_name, baseline_name, minimum, memory_limit, parity_policy in special_specs:
        before = baseline_rows.get(baseline_name)
        after = current_rows.get(current_name)
        if before is None or after is None:
            missing_special = [
                name
                for name, row in ((baseline_name, before), (current_name, after))
                if row is None
            ]
            errors.append(f"missing special performance workload(s): {missing_special}")
            special.append(
                {
                    "name": current_name,
                    "reference": baseline_name,
                    "missing_workloads": missing_special,
                    "parity_policy": parity_policy,
                    "pass": False,
                }
            )
            continue
        speedup = _time(before) / _time(after) if _time(after) > 0 else float("inf")
        memory_ratio = _memory(after) / max(_memory(before), 1)
        digest_match: bool | None = None
        if current_name == "epdm_semibatch_10000_steps_compiled":
            digest_match = before.get("result_sha256") == after.get("result_sha256")
        passed = speedup >= minimum and (memory_limit is None or memory_ratio <= memory_limit)
        if digest_match is False:
            passed = False
            errors.append(f"{current_name}: structured digest differs from scalar reference")
        if speedup < minimum:
            errors.append(
                f"{current_name}: speedup {speedup:.3f}x is below {minimum:.3f}x"
            )
        if memory_limit is not None and memory_ratio > memory_limit:
            errors.append(
                f"{current_name}: peak-memory ratio {memory_ratio:.3f} exceeds {memory_limit:.3f}"
            )
        special.append(
            {
                "name": current_name,
                "reference": baseline_name,
                "baseline_median_s": _time(before),
                "optimized_median_s": _time(after),
                "speedup": speedup,
                "minimum_speedup": minimum,
                "baseline_peak_memory_bytes": _memory(before),
                "optimized_peak_memory_bytes": _memory(after),
                "peak_memory_ratio": memory_ratio,
                "maximum_peak_memory_ratio": memory_limit,
                "result_digest_match": digest_match,
                "parity_policy": parity_policy,
                "pass": passed,
            }
        )

    scale_checks = [
        _scale_check(
            current_rows,
            small="epdm_three_level_64_site_families",
            large="epdm_three_level_512_site_families",
            size_ratio=8.0,
            limit=1.25,
        ),
        _scale_check(
            current_rows,
            small="process_package_500_equipment",
            large="process_package_5000_equipment",
            size_ratio=10.0,
            limit=1.25,
        ),
        _scale_check(
            current_rows,
            small="provenance_300_files_build_and_verify",
            large="provenance_3000_files_build_and_verify",
            size_ratio=10.0,
            limit=1.25,
        ),
    ]
    for check in scale_checks:
        if check["pass"]:
            continue
        if check["missing_workloads"]:
            errors.append(
                f"scale check {check['small']} -> {check['large']} is missing workloads: "
                f"{check['missing_workloads']}"
            )
        else:
            errors.append(
                f"scale check {check['small']} -> {check['large']} exceeded normalized limit"
            )

    return {
        "schema": "TSAO-PERFORMANCE-COMPARISON-2",
        "baseline_version": baseline.get("version"),
        "optimized_version": current.get("version"),
        "pass": not errors,
        "errors": errors,
        "common_workload_comparisons": comparisons,
        "optimized_path_comparisons": special,
        "scale_checks": scale_checks,
        "qualification_scope": "SOFTWARE_PERFORMANCE_ONLY",
        "scientific_technical_approval": "NOT_EVALUATED",
        "engineering_design_approval": "NOT_EVALUATED",
        "industrial_performance_guarantee": "NOT_EVALUATED",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare TSAO v2 performance reports")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = compare_reports(_load(args.baseline), _load(args.current))
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
