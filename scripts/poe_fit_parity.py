"""Hash-bound numerical evidence for the fixed 401-point first-order fit benchmark."""

from __future__ import annotations

import hashlib
import json
import math
from typing import Any

WORKLOAD = "poe_one_parameter_fit_401_points"
# Recomputed from the pre-expm1 implementation at 2ae9ce4ff46528def5bd4d187dced642f200da9f.
# Its complete JSON preimage matches the untouched alpha10 report's recorded SHA-256.
LEGACY_RESULT: dict[str, Any] = {
    "status": "CALCULATED_REFERENCE_ONLY",
    "rate_constant_s": 0.2,
    "objective": 0.0,
    "rmse": 0.0,
    "information_scalar": 616.4706945381237,
    "identifiable": True,
    "bounds_s": [0.01, 1.0],
    "scientific_approval": "NOT_EVALUATED",
}


def result_digest(result: object) -> str:
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _witness(row: dict[str, object]) -> tuple[dict[str, Any], str]:
    witness = row.get("result_witness")
    source = "measured-result-witness"
    if witness is None:
        if row.get("result_sha256") != result_digest(LEGACY_RESULT):
            raise ValueError("result witness is missing and no verified legacy preimage matches")
        witness = LEGACY_RESULT
        source = "verified-legacy-SHA256-preimage"
    if not isinstance(witness, dict):
        raise ValueError("result witness must be an object")
    if result_digest(witness) != row.get("result_sha256"):
        raise ValueError("result witness does not match the recorded SHA-256")
    expected_keys = set(LEGACY_RESULT)
    if set(witness) not in (expected_keys, expected_keys | {"time_design_varies"}):
        raise ValueError("unrecognized fit-result fields")
    if witness.get("status") != "CALCULATED_REFERENCE_ONLY":
        raise ValueError("fit status changed")
    if witness.get("scientific_approval") != "NOT_EVALUATED":
        raise ValueError("scientific approval boundary changed")
    if witness.get("identifiable") is not True or witness.get("bounds_s") != [0.01, 1.0]:
        raise ValueError("fit bounds or identifiability changed")
    if "time_design_varies" in witness and witness["time_design_varies"] is not True:
        raise ValueError("the fixed benchmark has varying observation times")
    for name in ("rate_constant_s", "objective", "rmse", "information_scalar"):
        value = witness[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be numeric")
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{name} must be finite and non-negative")
    # Known synthetic data: t_i = 0.05 i, y_i = 1 - exp(-0.2 t_i), i = 0,...,400.
    # These absolute residual bounds admit rounding error, not a changed fitted model.
    if abs(witness["rate_constant_s"] - 0.2) > 1e-12:
        raise ValueError("fitted rate differs from the analytical reference")
    if witness["rmse"] > 1e-12 or witness["objective"] > 401 * 1e-24:
        raise ValueError("fit residual exceeds the analytical-reference tolerance")
    if not math.isclose(
        witness["objective"], 401 * witness["rmse"] ** 2, rel_tol=1e-10, abs_tol=1e-30
    ):
        raise ValueError("objective and RMSE are inconsistent")
    information = math.fsum((0.05 * i) ** 2 * math.exp(-0.4 * 0.05 * i) for i in range(401))
    if not math.isclose(witness["information_scalar"], information, rel_tol=1e-12, abs_tol=0):
        raise ValueError("information differs from the analytical reference")
    return witness, source


def compare_fit_results(before: dict[str, object], after: dict[str, object]) -> dict[str, object]:
    """Validate both results independently; timing thresholds belong to the caller."""
    try:
        baseline, baseline_source = _witness(before)
        current, current_source = _witness(after)
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        return {"pass": False, "error": str(exc)}
    return {
        "pass": True,
        "contract": "poe-first-order-401-analytical-v1",
        "baseline_witness": baseline_source,
        "current_witness": current_source,
        "absolute_rate_difference": abs(current["rate_constant_s"] - baseline["rate_constant_s"]),
        "maximum_rmse": max(current["rmse"], baseline["rmse"]),
        "rate_absolute_tolerance": 1e-12,
        "rmse_absolute_tolerance": 1e-12,
        "information_relative_tolerance": 1e-12,
        "scientific_approval": "NOT_EVALUATED",
    }
