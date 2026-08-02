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

PARITY_POLICIES = {
    "doctor_core_repository": "repository semantic contract: PASS and approval boundaries",
    "process_package_500_equipment": (
        "process-package semantic contract: fail-closed topology, component, "
        "mass and energy gates"
    ),
    "process_package_5000_equipment": (
        "process-package semantic contract: fail-closed topology, component, "
        "mass and energy gates"
    ),
    "skillpack_inventory": (
        "skillpack semantic contract: four Skills, 14/6/6 inventory, "
        "README assets and approval boundaries"
    ),
    "wheel_content_verification": "wheel semantic contract: identity and required-member tests",
    "poe_dynamic_response_10000_points": "analytical response and metric tolerance contract",
    "poe_finite_difference_jacobian_8x200": "analytical Jacobian tolerance contract",
}

WORK_UNIT_NORMALIZED = {
    "doctor_core_repository": "schema_count",
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
        raw_ratio = _time(before) / _time(after) if _time(after) > 0 else float("inf")
        minimum = COMMON_MINIMUM_RATIO.get(name, 0.85)
        digest_match = before.get("result_sha256") == after.get("result_sha256")
        parity_policy = PARITY_POLICIES.get(name, "exact structured SHA-256")
        parity_pass = True if name in PARITY_POLICIES else digest_match
        timing_ratio = raw_ratio
        work_unit = WORK_UNIT_NORMALIZED.get(name)
        baseline_work_units: float | None = None
        optimized_work_units: float | None = None
        work_unit_error: str | None = None
        if work_unit is not None:
            try:
                baseline_work_units = float(before["work_units"])
                optimized_work_units = float(after["work_units"])
            except (KeyError, TypeError, ValueError):
                work_unit_error = (
                    f"{name}: missing numeric work_units for {work_unit} normalization"
                )
            else:
                if baseline_work_units <= 0 or optimized_work_units <= 0:
                    work_unit_error = (
                        f"{name}: work_units must be positive for {work_unit} normalization"
                    )
                elif before.get("work_unit") != work_unit or after.get("work_unit") != work_unit:
                    work_unit_error = (
                        f"{name}: work_unit identity mismatch for {work_unit} normalization"
                    )
                else:
                    timing_ratio = raw_ratio * optimized_work_units / baseline_work_units
        if work_unit_error is not None:
            errors.append(work_unit_error)
        timing_pass = work_unit_error is None and timing_ratio >= minimum
        passed = parity_pass and timing_pass
        if not parity_pass:
            errors.append(f"{name}: numerical result digest changed")
        if work_unit_error is None and timing_ratio < minimum:
            qualifier = "work-unit-normalized " if work_unit is not None else ""
            errors.append(
                f"{name}: {qualifier}performance ratio {timing_ratio:.3f}x "
                f"is below {minimum:.3f}x"
            )
        comparisons.append(
            {
                "name": name,
                "baseline_median_s": _time(before),
                "optimized_median_s": _time(after),
                "raw_performance_ratio": raw_ratio,
                "performance_ratio": timing_ratio,
                "minimum_ratio": minimum,
                "work_unit_normalized": work_unit is not None,
                "work_unit": work_unit,
                "baseline_work_units": baseline_work_units,
                "optimized_work_units": optimized_work_units,
                "baseline_peak_memory_bytes": _memory(before),
                "optimized_peak_memory_bytes": _memory(after),
                "result_digest_match": digest_match,
                "parity_policy": parity_policy,
                "parity_verified_by_tests": name in PARITY_POLICIES,
                "pass": passed,
            }
        )

    special_specs = (
        (
            "epdm_parameter_scan_1000_batch",
            "epdm_parameter_scan_1000_scalar",
            3.0,
            None,
            "scalar-vs-batch elementwise tolerance contract",
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
            "terminal/full final-state and metrics exact contract",
        ),
    )
    special: list[dict[str, object]] = []
    minimum_benefit_retention = 0.90
    minimum_path_ratio = 0.90
    for optimized_name, reference_name, target_speedup, memory_limit, parity_policy in special_specs:
        baseline_reference = baseline_rows.get(reference_name)
        baseline_optimized = baseline_rows.get(optimized_name)
        current_reference = current_rows.get(reference_name)
        current_optimized = current_rows.get(optimized_name)
        rows = (
            (f"baseline:{reference_name}", baseline_reference),
            (f"baseline:{optimized_name}", baseline_optimized),
            (f"current:{reference_name}", current_reference),
            (f"current:{optimized_name}", current_optimized),
        )
        missing_special = [label for label, row in rows if row is None]
        if missing_special:
            errors.append(f"missing special performance workload(s): {missing_special}")
            special.append(
                {
                    "name": optimized_name,
                    "reference": reference_name,
                    "missing_workloads": missing_special,
                    "parity_policy": parity_policy,
                    "pass": False,
                }
            )
            continue
        assert baseline_reference is not None
        assert baseline_optimized is not None
        assert current_reference is not None
        assert current_optimized is not None
        baseline_speedup = (
            _time(baseline_reference) / _time(baseline_optimized)
            if _time(baseline_optimized) > 0
            else float("inf")
        )
        current_speedup = (
            _time(current_reference) / _time(current_optimized)
            if _time(current_optimized) > 0
            else float("inf")
        )
        effective_minimum_speedup = min(
            target_speedup,
            baseline_speedup * minimum_benefit_retention,
        )
        benefit_retention = (
            current_speedup / baseline_speedup
            if baseline_speedup > 0
            else float("inf")
        )
        optimized_path_ratio = (
            _time(baseline_optimized) / _time(current_optimized)
            if _time(current_optimized) > 0
            else float("inf")
        )
        memory_ratio = _memory(current_optimized) / max(_memory(current_reference), 1)
        digest_match: bool | None = None
        if optimized_name == "epdm_semibatch_10000_steps_compiled":
            digest_match = (
                current_reference.get("result_sha256")
                == current_optimized.get("result_sha256")
            )
        passed = (
            current_speedup >= effective_minimum_speedup
            and benefit_retention >= minimum_benefit_retention
            and optimized_path_ratio >= minimum_path_ratio
            and (memory_limit is None or memory_ratio <= memory_limit)
        )
        if digest_match is False:
            passed = False
            errors.append(f"{optimized_name}: structured digest differs from current scalar reference")
        if current_speedup < effective_minimum_speedup:
            errors.append(
                f"{optimized_name}: speedup {current_speedup:.3f}x is below "
                f"effective {effective_minimum_speedup:.3f}x "
                f"(configured target {target_speedup:.3f}x; "
                f"parent baseline {baseline_speedup:.3f}x)"
            )
        if benefit_retention < minimum_benefit_retention:
            errors.append(
                f"{optimized_name}: speedup retention {benefit_retention:.3f}x is below "
                f"{minimum_benefit_retention:.3f}x"
            )
        if optimized_path_ratio < minimum_path_ratio:
            errors.append(
                f"{optimized_name}: same-path performance ratio "
                f"{optimized_path_ratio:.3f}x is below {minimum_path_ratio:.3f}x"
            )
        if memory_limit is not None and memory_ratio > memory_limit:
            errors.append(
                f"{optimized_name}: peak-memory ratio {memory_ratio:.3f} exceeds "
                f"{memory_limit:.3f}"
            )
        special.append(
            {
                "name": optimized_name,
                "reference": reference_name,
                "baseline_reference_median_s": _time(baseline_reference),
                "baseline_optimized_median_s": _time(baseline_optimized),
                "current_reference_median_s": _time(current_reference),
                "current_optimized_median_s": _time(current_optimized),
                "baseline_speedup": baseline_speedup,
                "speedup": current_speedup,
                "configured_minimum_speedup": target_speedup,
                "effective_minimum_speedup": effective_minimum_speedup,
                "speedup_retention": benefit_retention,
                "minimum_speedup_retention": minimum_benefit_retention,
                "same_path_performance_ratio": optimized_path_ratio,
                "minimum_same_path_performance_ratio": minimum_path_ratio,
                "current_reference_peak_memory_bytes": _memory(current_reference),
                "current_optimized_peak_memory_bytes": _memory(current_optimized),
                "peak_memory_ratio": memory_ratio,
                "maximum_peak_memory_ratio": memory_limit,
                "result_digest_match": digest_match,
                "parity_policy": parity_policy,
                "parity_verified_by_tests": digest_match is True
                or optimized_name != "epdm_semibatch_10000_steps_compiled",
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
