"""Public numerical entry points must not approve non-representable balances."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

import skills.poe.material_balance as balance_module
from skills.poe.core import audit_process_package, qualify_property_method, validate_process_case
from skills.poe.material_balance import check_component_rows
from tsao.contracts_v17 import Quantity
from tsao.contracts_v17 import component_balance as balance_v17
from tsao.process_general import (
    FARADAY_C_MOL,
    availability,
    cstr_first_order_conversion,
    faradaic_efficiency,
    oxygen_transfer_rate,
    pfr_first_order_conversion,
    process_capability_index,
    recycle_impurity_steady_state,
    semibatch_accumulation,
    supersaturation_ratio,
    weibull_reliability,
)
from tsao.scientific_contracts_v16 import Flow
from tsao.scientific_contracts_v16 import component_balance as balance_v16

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "poe_package_numeric_fixture", ROOT / "skills/poe/tests/test_poe_alpha6_package.py"
)
FIXTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURE)


def stream(name: str, source: str, target: str, flow: float) -> dict:
    return {
        "stream_id": name,
        "from": source,
        "to": target,
        "flow_kg_h": flow,
        "composition": {"ethylene": 0.1, "solvent": 0.9},
    }


def case_with_streams(streams: list[dict]) -> dict:
    case = FIXTURE.process_case()
    case["streams"] = streams
    return case


@pytest.mark.parametrize("destination", ["feed", "product", "loss"])
def test_poe_public_case_rejects_overflowed_totals_as_strict_json(destination: str) -> None:
    streams = [stream("F", "EXTERNAL", "R1", 1e308), stream("P", "R1", "EXTERNAL", 1e308)]
    source, target = {
        "feed": ("EXTERNAL", "R1"),
        "product": ("R1", "EXTERNAL"),
        "loss": ("R1", "LOSS"),
    }[destination]
    streams.append(stream("X1", source, target, 1e308))
    if destination == "loss":
        streams.append(stream("X2", source, target, 1e308))
    result = validate_process_case(case_with_streams(streams))
    assert result["status"] == "FAIL" and result["pass"] is False
    assert any("mass balance arithmetic" in message for message in result["errors"])
    assert result["metrics"]["mass_balance_residual_fraction"] is None
    json.dumps(result, allow_nan=False)


def test_poe_public_case_rejects_underflowed_nonzero_relative_residual() -> None:
    case = case_with_streams(
        [
            stream("F", "EXTERNAL", "R1", 1e308),
            stream("P", "R1", "EXTERNAL", 1e308),
            stream("L", "R1", "LOSS", 1e-100),
        ]
    )
    case["mass_balance_tolerance_fraction"] = 0.0
    result = validate_process_case(case)
    assert result["status"] == "FAIL"
    assert any("representable nonzero finite range" in message for message in result["errors"])
    json.dumps(result, allow_nan=False)


def test_poe_public_case_preserves_large_representable_closure_and_real_imbalance() -> None:
    case = case_with_streams(
        [
            stream("F1", "EXTERNAL", "R1", 8e307),
            stream("F2", "EXTERNAL", "R1", 8e307),
            stream("P", "R1", "EXTERNAL", 1.6e308),
        ]
    )
    assert validate_process_case(case)["status"] == "PASS"
    case["streams"][-1]["flow_kg_h"] = 8e307
    result = validate_process_case(case)
    assert result["status"] == "HOLD"
    assert result["metrics"]["mass_balance_residual_fraction"] == 0.5


def test_poe_huge_integer_is_a_structured_failure() -> None:
    case = case_with_streams([stream("F", "EXTERNAL", "R1", 10**400)])
    assert validate_process_case(case)["status"] == "FAIL"
    property_method = FIXTURE.qualified_property()
    property_method["error_metrics"] = {"density_relative": 10**400}
    assert qualify_property_method(property_method)["status"] == "FAIL"


def test_poe_package_with_valid_file_digests_cannot_hide_process_overflow(tmp_path: Path) -> None:
    root = tmp_path / "package"
    FIXTURE.build_manifested_package(root)
    assert audit_process_package(root)["status"] == "PASS"
    process_path = root / "process_case.json"
    process = json.loads(process_path.read_text(encoding="utf-8"))
    process["streams"] = [
        stream("F1", "EXTERNAL", "R1", 1e308),
        stream("F2", "EXTERNAL", "R1", 1e308),
        stream("P", "R1", "EXTERNAL", 1e308),
    ]
    process_path.write_text(json.dumps(process), encoding="utf-8")
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    data = process_path.read_bytes()
    manifest["structured_record_integrity"]["process_case"].update(
        sha256=hashlib.sha256(data).hexdigest(), bytes=len(data)
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = audit_process_package(root)
    assert result["status"] == "FAIL"
    assert any("mass balance arithmetic" in message for message in result["errors"])
    assert not any("mismatch" in message for message in result["errors"])
    json.dumps(result, allow_nan=False)


def flow16(value: float, scale: float = 1.0) -> Flow:
    return Flow(value, "kg/s", "mass", scale)


def flow17(value: float, scale: float = 1.0) -> Quantity:
    return Quantity(value, "kg/s", "mass_flow", scale)


@pytest.mark.parametrize("version", [16, 17])
@pytest.mark.parametrize("value,scale", [(1e308, 2.0), (1e-300, 1e-100), (10**400, 1.0)])
def test_compatibility_balances_reject_unrepresentable_canonical_flow(
    version: int, value: float, scale: float
) -> None:
    with pytest.raises(ValueError):
        if version == 16:
            balance_v16({"A": flow16(value, scale)}, {}, atol=0.0, rtol=1e-6)
        else:
            balance_v17(
                {"A": flow17(value, scale)}, {}, absolute_tolerance=0.0, relative_tolerance=1e-6
            )


@pytest.mark.parametrize("version", [16, 17])
def test_compatibility_balances_reject_overflowed_tolerance(version: int) -> None:
    with pytest.raises(ValueError):
        if version == 16:
            balance_v16({"A": flow16(1e308)}, {}, atol=0.0, rtol=2.0)
        else:
            balance_v17({"A": flow17(1e308)}, {}, absolute_tolerance=0.0, relative_tolerance=2.0)


def test_v16_preserves_finite_residual_after_large_cancellation() -> None:
    result = balance_v16(
        {"A": flow16(1e308)},
        {"A": flow16(1e308)},
        generation={"A": flow16(1e308)},
        accumulation={"A": flow16(1e308)},
        atol=0.0,
        rtol=0.0,
    )
    assert result == {"status": "PASS", "residuals": {"A": 0.0}, "failed_components": []}


def test_v17_preserves_finite_residual_after_intermediate_overflow() -> None:
    result = balance_v17(
        {"A": flow17(1e308)},
        {"A": flow17(1e308)},
        sources={"A": flow17(1e308)},
        absolute_tolerance=0.0,
        relative_tolerance=0.0,
    )
    assert result.status == "FAIL" and result.residuals == {"A": 1e308}


def test_compatibility_absolute_tolerance_and_scale_conventions_are_unchanged() -> None:
    assert balance_v16({"A": flow16(1e-6)}, {}, atol=1e-5, rtol=0.0)["status"] == "PASS"
    assert balance_v16({"A": flow16(1e-6)}, {}, atol=0.0, rtol=0.0)["status"] == "FAIL"
    assert (
        balance_v17({"A": flow17(1e-6)}, {}, absolute_tolerance=0.0, relative_tolerance=1e-5).status
        == "PASS"
    )
    assert (
        balance_v17({"A": flow17(1e-6)}, {}, absolute_tolerance=0.0, relative_tolerance=0.0).status
        == "FAIL"
    )


@pytest.mark.parametrize("magnitude", [1e-300, 1.0, 1e308])
def test_availability_is_half_for_equal_positive_times(magnitude: float) -> None:
    assert availability(magnitude, magnitude) == 0.5


@pytest.mark.parametrize("reactor", [cstr_first_order_conversion, pfr_first_order_conversion])
def test_bounded_conversion_preserves_saturation_and_small_nonzero_values(reactor) -> None:
    assert reactor(1e308, 2.0) == 1.0
    assert reactor(1e-300, 1.0) == 1e-300
    assert reactor(0.0, 1e308) == 0.0
    with pytest.raises(ValueError):
        reactor(1e-300, 1e-100)


@pytest.mark.parametrize("scale", [1e-300, 1.0, 1e308])
def test_faradaic_ratio_preserves_cancelling_large_and_small_charge_scales(scale: float) -> None:
    assert faradaic_efficiency(scale, 1.0, scale, 1e6) == pytest.approx(FARADAY_C_MOL / 1e6)


def test_capability_ratio_avoids_overflowing_sigma_and_differences() -> None:
    assert process_capability_index(0.0, 1e308, -1e308, 1e308) == pytest.approx(1 / 3)
    assert process_capability_index(-1e308, 1e308, -1.5e308, 1e308) == pytest.approx(1 / 6)


@pytest.mark.parametrize(
    "operation",
    [
        lambda: availability(1e-300, 1e308),
        lambda: faradaic_efficiency(1e-300, 1.0, 1e308, 1e100),
        lambda: oxygen_transfer_rate(1e-300, 1e-100, 0.0),
        lambda: oxygen_transfer_rate(1e308, 2.0, 0.0),
        lambda: supersaturation_ratio(1e-300, 1e100),
        lambda: supersaturation_ratio(1e308, 1e-100),
        lambda: recycle_impurity_steady_state(1e308, 0.9, 0.0),
        lambda: semibatch_accumulation(1e-300, 0.0, 1e-100),
        lambda: semibatch_accumulation(1e308, 0.0, 2.0),
        lambda: weibull_reliability(1000.0, 1.0, 1.0),
        lambda: process_capability_index(0.0, 1e308, -1e-300, 1e-300),
    ],
)
def test_process_general_rejects_unrepresentable_nonzero_results(operation) -> None:
    with pytest.raises(ValueError):
        operation()


def test_zero_physical_results_remain_valid() -> None:
    assert oxygen_transfer_rate(0.0, 1.0, 0.0) == 0.0
    assert faradaic_efficiency(0.0, 1.0, 1.0, 1.0) == 0.0
    assert semibatch_accumulation(1e308, 1e308, 1e308) == 0.0
    assert weibull_reliability(0.0, 1.0, 1.0) == 1.0
    assert process_capability_index(0.0, 1.0, 0.0, 1.0) == 0.0
    assert math.isfinite(availability(1e308, 1e-300))


def test_weibull_bounded_result_survives_extreme_intermediate_scales() -> None:
    assert weibull_reliability(1e-300, 1.0, 2.0) == 1.0
    assert weibull_reliability(1e308, 1e-308, 1e-300) == pytest.approx(math.exp(-1.0))
    assert weibull_reliability(1e-308, 1e308, 1e-300) == pytest.approx(math.exp(-1.0))


def csv_row(**changes: str) -> dict[str, str]:
    row = {
        "component": "A",
        "quantity_basis": "mass",
        "quantity_unit": "kg",
        "time_unit": "s",
        "in": "0",
        "out": "0",
        "generation": "0",
        "consumption": "0",
        "accumulation": "0",
        "absolute_tolerance": "0",
        "relative_tolerance": "0",
        "reference_scale": "1",
    }
    row.update(changes)
    return row


def test_csv_adapter_rejects_unit_conversion_underflow_but_keeps_subnormal_flows() -> None:
    with pytest.raises(ValueError, match="nonzero"):
        check_component_rows([csv_row(**{"in": "5e-324", "time_unit": "h"})])
    result = check_component_rows([csv_row(**{"in": "5e-324"})])
    assert result["status"] == "FAIL"
    assert result["components"][0]["incoming"] == 5e-324


def test_csv_adapter_retains_small_residual_across_large_cancellation() -> None:
    result = check_component_rows(
        [csv_row(**{"in": "1e308", "generation": "1", "consumption": "1e308"})]
    )
    assert result["status"] == "FAIL"
    assert result["components"][0]["residual"] == -1.0
    assert result["total"]["residual"] == -1.0
    json.dumps(result, allow_nan=False)


def test_csv_adapter_retains_finite_balance_after_intermediate_overflow() -> None:
    result = check_component_rows(
        [
            csv_row(
                **{
                    "in": "1e308",
                    "generation": "1e308",
                    "consumption": "1e308",
                    "accumulation": "1e308",
                }
            )
        ]
    )
    assert result["status"] == "PASS"
    assert result["total"]["residual"] == 0.0
    json.dumps(result, allow_nan=False)


def test_csv_adapter_rejects_unrepresentable_total_tolerance() -> None:
    rows = [
        csv_row(
            component=name,
            absolute_tolerance="5e307",
            relative_tolerance="1",
            reference_scale="5e307",
        )
        for name in ("A", "B")
    ]
    with pytest.raises(ValueError):
        check_component_rows(rows)


def test_csv_cli_rejects_nonzero_conversion_underflow(tmp_path: Path) -> None:
    row = csv_row(**{"in": "5e-324", "time_unit": "h"})
    path = tmp_path / "nonzero-flow.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)
    source_root = Path(balance_module.__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            str(source_root / "skills/polymer-general/scripts/check_balance.py"),
            str(path),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 2
    assert "nonzero" in result.stderr
    assert '"status": "PASS"' not in result.stdout
