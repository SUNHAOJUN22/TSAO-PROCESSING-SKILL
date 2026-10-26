"""Measure only the corrected POE workloads in a pinned, clean source worktree.

No recorded duration, digest, memory value or PASS flag is invented. The three
rows are replaced by actual same-interpreter measurements; all superseded rows
remain in the receipt and all unrelated workload rows are preserved verbatim.
"""

from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.poe_kinetics_benchmark_contract import (  # noqa: E402
    MODEL_ID,
    POE_MASS_MOMENT_BASELINE_COMMIT,
    STATE_FIELDS,
    WORKLOADS,
    workload_identity,
)

_MEASURE_PROGRAM = """
import json, sys
sys.path.insert(0, '.')
from scripts.benchmark_performance import BenchmarkCase, _measure, _poe_rk4_case
from scripts.benchmark_performance_v2 import _poe_rk4_terminal_10000
from skills.poe.kinetics import KineticState
cases = (
    BenchmarkCase('poe_rk4_400_steps', lambda: _poe_rk4_case(400), 3, 1),
    BenchmarkCase('poe_rk4_10000_steps', lambda: _poe_rk4_case(10000), 1, 1,
                  warmups=1, repeat_override=3),
    BenchmarkCase('poe_rk4_10000_steps_terminal', _poe_rk4_terminal_10000, 1, 1,
                  warmups=1, repeat_override=3),
)
print(json.dumps({'state_fields': list(KineticState.__dataclass_fields__),
                  'benchmarks': [_measure(case, repeats=int(sys.argv[1])) for case in cases]},
                 allow_nan=False))
"""


def measure_baseline(worktree: Path, *, repeats: int) -> list[dict[str, object]]:
    if repeats < 3:
        raise ValueError("repeats must be at least 3")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
    if head != POE_MASS_MOMENT_BASELINE_COMMIT:
        raise ValueError("POE scientific baseline commit does not match the pinned source")
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"], cwd=worktree, text=True
    )
    if dirty.strip():
        raise ValueError("POE scientific baseline contains tracked modifications")
    measured = json.loads(
        subprocess.check_output(
            [sys.executable, "-c", _MEASURE_PROGRAM, str(repeats)], cwd=worktree, text=True
        )
    )
    if measured.get("state_fields") != list(STATE_FIELDS):
        raise ValueError("POE scientific baseline does not implement the 13-state model")
    rows = measured["benchmarks"]
    for row in rows:
        row["workload_identity"] = workload_identity(row["name"])
        row["source_commit"] = head
    return rows


def replace_poe_rows(
    report: dict[str, object], measured: list[dict[str, object]]
) -> dict[str, object]:
    result = copy.deepcopy(report)
    old_rows = result.get("benchmarks")
    if not isinstance(old_rows, list):
        raise ValueError("performance report must have a benchmarks list")
    replacements = {row["name"]: row for row in measured}
    targets = [row for row in old_rows if row.get("name") in WORKLOADS]
    if len(measured) != len(WORKLOADS) or set(replacements) != set(WORKLOADS):
        raise ValueError("measured POE workloads must each occur exactly once")
    if len(targets) != len(WORKLOADS) or {row["name"] for row in targets} != set(WORKLOADS):
        raise ValueError("original report must contain each POE workload exactly once")
    for name, row in replacements.items():
        if row.get("source_commit") != POE_MASS_MOMENT_BASELINE_COMMIT:
            raise ValueError("measured row is not bound to the pinned POE source")
        if row.get("workload_identity") != workload_identity(name):
            raise ValueError("measured row does not have the corrected POE workload identity")
    result["benchmarks"] = [copy.deepcopy(replacements.get(row["name"], row)) for row in old_rows]
    result["poe_mass_moment_baseline_receipt"] = {
        "source_commit": POE_MASS_MOMENT_BASELINE_COMMIT,
        "model_id": MODEL_ID,
        "reason": "Correct Mw needs two mass second moments; old 11-state timings and results are not comparable.",
        "superseded_baseline_rows": targets,
        "measurement": "SAME_INTERPRETER_SAME_RUNNER_SAME_REPETITIONS",
        "scientific_approval": "NOT_EVALUATED",
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--worktree", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=7)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    updated = replace_poe_rows(report, measure_baseline(args.worktree, repeats=args.repeats))
    temporary = args.report.with_name(f".{args.report.name}.tmp")
    temporary.write_text(json.dumps(updated, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
