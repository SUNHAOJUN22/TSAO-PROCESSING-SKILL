from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.benchmark_performance import BenchmarkCase, _measure, _poe_one_parameter_fit_case
from scripts.compare_performance_v2 import _common_comparisons
from scripts.poe_fit_parity import LEGACY_RESULT, WORKLOAD, compare_fit_results, result_digest


def row(result: object, *, witness: bool = True, seconds: float = 1.0) -> dict[str, object]:
    return {
        "name": WORKLOAD,
        "median_s_per_call": seconds,
        "peak_memory_bytes": 1,
        "result_sha256": result_digest(result),
        **({"result_witness": result} if witness else {}),
    }


def test_legacy_preimage_matches_unchanged_historical_report() -> None:
    path = Path(__file__).resolve().parents[1] / "reports/PERFORMANCE_BASELINE_ALPHA10_EXTENDED.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    legacy = next(item for item in report["benchmarks"] if item["name"] == WORKLOAD)
    assert legacy["result_sha256"] == result_digest(LEGACY_RESULT)
    current = row(_poe_one_parameter_fit_case())
    assert compare_fit_results(legacy, current)["pass"] is True


def test_measurement_binds_witness_without_projecting_away_original_fields() -> None:
    measured = _measure(BenchmarkCase(WORKLOAD, _poe_one_parameter_fit_case, 1, 1), repeats=1)
    assert measured["result_sha256"] == result_digest(measured["result_witness"])
    assert measured["result_witness"]["time_design_varies"] is True
    assert measured["result_sha256"] != result_digest(LEGACY_RESULT)


@pytest.mark.parametrize("historical", [False, True])
def test_verified_numeric_parity_does_not_disable_timing_gate(historical: bool) -> None:
    baseline = row(LEGACY_RESULT, witness=False)
    current = row(_poe_one_parameter_fit_case(), seconds=2.0)
    errors: list[str] = []
    unavailable: list[str] = []
    compared = _common_comparisons(
        {WORKLOAD: baseline},
        {WORKLOAD: current},
        historical=historical,
        errors=errors,
        not_applicable=unavailable,
    )[0]
    assert compared["numerical_result_evidence"]["pass"] is True
    assert compared["result_digest_match"] is False
    assert compared["pass"] is False
    assert compared["historical_status"] == "FAIL"
    assert compared["minimum_ratio"] == 0.90
    assert any("performance ratio" in error for error in errors)
    assert unavailable == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("rate_constant_s", 0.21),
        ("rmse", 0.001),
        ("objective", 1.0),
        ("information_scalar", 500.0),
        ("identifiable", False),
        ("scientific_approval", "PASS"),
        ("bounds_s", [0.0, 10.0]),
        ("status", "PASS"),
        ("time_design_varies", False),
        ("new_unknown_field", True),
        ("rate_constant_s", True),
    ],
)
def test_changed_result_cannot_pass_even_with_matching_recomputed_digest(field, value) -> None:
    altered = copy.deepcopy(LEGACY_RESULT)
    altered[field] = value
    bad = row(altered)
    assert compare_fit_results(bad, bad)["pass"] is False


def test_wrong_hash_and_missing_unknown_witness_fail_closed() -> None:
    baseline = row(LEGACY_RESULT)
    wrong_hash = row(_poe_one_parameter_fit_case())
    wrong_hash["result_sha256"] = "a" * 64
    assert compare_fit_results(baseline, wrong_hash)["pass"] is False
    assert compare_fit_results(baseline, {"result_sha256": "b" * 64})["pass"] is False


def test_nonfinite_and_inconsistent_residual_witnesses_fail_closed() -> None:
    bad = copy.deepcopy(LEGACY_RESULT)
    bad["rate_constant_s"] = float("nan")
    assert compare_fit_results(row(LEGACY_RESULT), {"result_witness": bad})["pass"] is False
    bad = copy.deepcopy(LEGACY_RESULT)
    bad["objective"] = 1e-24
    assert compare_fit_results(row(LEGACY_RESULT), row(bad))["pass"] is False
