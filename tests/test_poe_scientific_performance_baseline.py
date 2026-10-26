from __future__ import annotations

import copy
from pathlib import Path

import pytest

from scripts.compare_performance_v2 import _common_comparisons
from scripts.poe_kinetics_benchmark_contract import (
    LEGACY_RESULT_DIGESTS,
    POE_MASS_MOMENT_BASELINE_COMMIT,
    WORKLOADS,
    workload_identity,
)
from scripts.rebase_poe_performance import measure_baseline, replace_poe_rows


def _row(name):
    return {
        "name": name,
        "median_s_per_call": 1.0,
        "peak_memory_bytes": 1000,
        "result_sha256": "a" * 64,
        "source_commit": POE_MASS_MOMENT_BASELINE_COMMIT,
        "workload_identity": workload_identity(name),
    }


def _compare(before, after, *, historical=False):
    errors, skipped = [], []
    rows = _common_comparisons(
        {before["name"]: before},
        {after["name"]: after},
        historical=historical,
        errors=errors,
        not_applicable=skipped,
    )
    return rows[0], errors, skipped


def test_scientific_rebase_replaces_only_measured_poe_rows_and_preserves_receipt():
    unrelated = {"name": "another_workload", "result_sha256": "unchanged", "median_s_per_call": 7.0}
    old = [{"name": name, "median_s_per_call": 9.0} for name in WORKLOADS]
    original = {"benchmarks": [unrelated, *old], "source_commit": "original-parent"}
    frozen = copy.deepcopy(original)
    updated = replace_poe_rows(original, [_row(name) for name in WORKLOADS])
    assert original == frozen
    assert updated["benchmarks"][0] == unrelated
    assert updated["source_commit"] == "original-parent"
    assert updated["poe_mass_moment_baseline_receipt"]["superseded_baseline_rows"] == old
    assert all(row["median_s_per_call"] == 1.0 for row in updated["benchmarks"][1:])


@pytest.mark.parametrize("fault", ["missing", "duplicate", "wrong_source", "wrong_model"])
def test_scientific_rebase_rejects_incomplete_or_unbound_rows(fault):
    rows = [_row(name) for name in WORKLOADS]
    original = {"benchmarks": copy.deepcopy(rows)}
    if fault == "missing":
        rows.pop()
    elif fault == "duplicate":
        rows[1] = rows[0]
    elif fault == "wrong_source":
        rows[0]["source_commit"] = "0" * 40
    else:
        rows[0]["workload_identity"]["step_s"] = 1.0
    with pytest.raises(ValueError):
        replace_poe_rows(original, rows)


def test_model_metadata_cannot_waive_changed_result_or_timing_threshold():
    before = _row("poe_rk4_10000_steps")
    changed = {**before, "result_sha256": "b" * 64}
    assert _compare(before, changed)[0]["pass"] is False
    slow = {**before, "median_s_per_call": 2.0}
    compared, errors, _ = _compare(before, slow)
    assert compared["minimum_ratio"] == 0.90
    assert compared["pass"] is False
    assert any("performance ratio" in error for error in errors)


def test_changed_or_removed_workload_identity_fails_even_when_result_hash_matches():
    before = _row("poe_rk4_400_steps")
    changed = copy.deepcopy(before)
    changed["workload_identity"]["duration_s"] = 1.0
    assert _compare(before, changed)[0]["pass"] is False
    changed.pop("workload_identity")
    assert _compare(before, changed)[0]["pass"] is False


def test_only_verified_old_model_is_historically_inapplicable():
    name = "poe_rk4_400_steps"
    before = _row(name)
    before.pop("workload_identity")
    before["result_sha256"] = LEGACY_RESULT_DIGESTS[name]
    after = _row(name)
    row, errors, skipped = _compare(before, after, historical=True)
    assert row["historical_status"] == "NOT_APPLICABLE"
    assert row["pass"] is None
    assert skipped and not errors
    assert _compare(before, after)[0]["pass"] is False
    before["result_sha256"] = "unknown-old-result"
    assert _compare(before, after, historical=True)[0]["pass"] is False


def test_measurement_rejects_the_wrong_source_before_running_benchmarks(monkeypatch):
    monkeypatch.setattr(
        "scripts.rebase_poe_performance.subprocess.check_output", lambda *a, **k: "wrong\n"
    )
    with pytest.raises(ValueError, match="pinned source"):
        measure_baseline(Path("unused"), repeats=7)


def test_measurement_rejects_modified_baseline_before_running_benchmarks(monkeypatch):
    outputs = iter([POE_MASS_MOMENT_BASELINE_COMMIT + "\n", " M skills/poe/kinetics.py\n"])
    monkeypatch.setattr(
        "scripts.rebase_poe_performance.subprocess.check_output", lambda *a, **k: next(outputs)
    )
    with pytest.raises(ValueError, match="tracked modifications"):
        measure_baseline(Path("unused"), repeats=7)


def test_workflow_keeps_original_baseline_and_measures_corrected_poe_source():
    text = (Path(__file__).resolve().parents[1] / ".github/workflows/ci.yml").read_text()
    assert 'PERFORMANCE_BASELINE_COMMIT: "8719e59140202aae53cdfb80239b80dedad6767a"' in text
    assert f'POE_MASS_MOMENT_BASELINE_COMMIT: "{POE_MASS_MOMENT_BASELINE_COMMIT}"' in text
    assert "python scripts/rebase_poe_performance.py" in text
