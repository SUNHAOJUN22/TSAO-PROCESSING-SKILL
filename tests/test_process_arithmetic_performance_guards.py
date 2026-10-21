"""Numeric and public-entry invariants behind process arithmetic fast paths."""

from __future__ import annotations

import importlib.util
import math
import random
import struct
from fractions import Fraction
from pathlib import Path

import pytest

from tsao.numeric_contract import finite, finite_product, finite_sum
from tsao.process_package import validate_process_package

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "process_arithmetic_fixture",
    ROOT / "skills/process-general/tests/test_process_package_runtime.py",
)
FIXTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FIXTURE)


def unchanged_stream_package():
    package = FIXTURE.valid_package()
    package["streams"][1]["enthalpy_kW"] = package["streams"][0]["enthalpy_kW"]
    package["equipment"][0]["duty_kW"] = 0.0
    return package


@pytest.mark.parametrize("operation", ["multiply", "divide"])
def test_single_operation_matches_exact_binary_rational_oracle(operation):
    rng = random.Random(20261021)
    pairs = [(0.0, 1.0), (-0.0, -1.0), (5e-324, 1.0), (1e308, 1e308), (5e-324, 0.5)]
    while len(pairs) < 300:
        left, right = (struct.unpack("!d", rng.randbytes(8))[0] for _ in range(2))
        if math.isfinite(left) and math.isfinite(right) and right != 0:
            pairs.append((left, right))
    for left, right in pairs:
        exact = (
            Fraction(left) * Fraction(right)
            if operation == "multiply"
            else Fraction(left) / Fraction(right)
        )
        try:
            expected = float(exact)
        except OverflowError:
            expected = math.inf
        kwargs = {} if operation == "multiply" else {"divisor": right}
        args = (left, right) if operation == "multiply" else (left,)
        if not math.isfinite(expected) or expected == 0 and exact != 0:
            with pytest.raises(ValueError, match="finite range"):
                finite_product(*args, **kwargs)
        else:
            assert finite_product(*args, **kwargs) == expected


@pytest.mark.parametrize("value", [True, None, float("nan"), float("inf"), "1e-999", 10**400])
def test_zero_product_does_not_hide_invalid_second_factor(value):
    with pytest.raises(ValueError):
        finite_product(0.0, value)
    with pytest.raises(ValueError):
        finite(value)


def test_general_product_retains_compensating_scale_and_zero_divisor_guards():
    assert finite_product(1e308, 1e308, divisor=1e308) == 1e308
    assert finite_product(5e-324, 0.5, divisor=0.5) == 5e-324
    assert finite_product(1e308, 1e308, 0.0) == 0.0
    with pytest.raises(ValueError, match="zero divisor"):
        finite_product(0.0, divisor=0.0)
    with pytest.raises(ValueError, match="finite"):
        finite_product(1e308, 1e308)
    with pytest.raises(ValueError, match="finite"):
        finite_product(5e-324, 0.5)


def test_identical_stream_and_general_balance_paths_have_identical_reports():
    package = unchanged_stream_package()
    direct = validate_process_package(package)
    assert direct["status"] == "PASS"
    package["equipment"][0].update(
        generation_kg_h={"A": 0.0},
        consumption_kg_h={"A": 0.0},
        reaction_basis={"description": "synthetic zero source and sink"},
    )
    assert validate_process_package(package) == direct


@pytest.mark.parametrize(
    "damage",
    ["decision", "topology", "evidence", "duty", "generation", "reaction", "composition", "mass"],
)
def test_identical_streams_do_not_bypass_other_audit_gates(damage):
    package = unchanged_stream_package()
    equipment = package["equipment"][0]
    if damage == "decision":
        equipment["design_status"] = "FAIL"
    elif damage == "topology":
        package["streams"][0]["destination"] = "UNKNOWN"
    elif damage == "evidence":
        package["streams"][0]["evidence_ids"] = ["UNKNOWN"]
    elif damage == "duty":
        equipment["duty_kW"] = math.nan
    elif damage == "generation":
        equipment["generation_kg_h"] = {"A": math.inf}
    elif damage == "reaction":
        equipment["reaction_basis"] = {"unrecognized_field": "incomplete"}
    elif damage == "composition":
        for stream in package["streams"]:
            stream["composition"] = {"A": "1e-999"}
    elif damage == "mass":
        for stream in package["streams"]:
            stream["total_mass_kg_h"] = math.inf
    result = validate_process_package(package)
    assert result["status"] == ("HOLD" if damage == "reaction" else "FAIL")
    assert not result["pass"]


@pytest.mark.parametrize("field", ["total_mass_kg_h", "enthalpy_kW"])
def test_repeated_audit_detects_one_ulp_change_in_previously_identical_stream(field):
    package = unchanged_stream_package()
    package["tolerances"] = {"mass_relative": 0.0, "energy_relative": 0.0}
    assert validate_process_package(package)["status"] == "PASS"
    value = package["streams"][1][field]
    package["streams"][1][field] = math.nextafter(value, math.inf)
    result = validate_process_package(package)
    assert result["status"] == "FAIL"
    package["streams"][1][field] = value
    assert validate_process_package(package)["status"] == "PASS"


def test_multi_stream_enthalpy_cancellation_preserves_nonzero_residual():
    package = unchanged_stream_package()
    original = package["streams"][0]
    inlet_values = [1e308, 1e308, 1.0, -1e308, -1e308]
    inlets = [
        {**original, "stream_id": f"IN-{index}", "total_mass_kg_h": 20.0, "enthalpy_kW": value}
        for index, value in enumerate(inlet_values)
    ]
    package["streams"] = [*inlets, {**package["streams"][1], "enthalpy_kW": 0.0}]
    package["equipment"][0]["inlet_stream_ids"] = [item["stream_id"] for item in inlets]
    result = validate_process_package(package)
    assert result["status"] == "FAIL"
    assert "ENERGY_BALANCE_FAILURE" in result["reason_codes"]
    assert result["metrics"]["max_energy_balance_relative_error"] == 1.0
    assert finite_sum([1e308, 1e308, 5e-324, -1e308, -1e308]) == 5e-324


def test_composition_sum_retains_small_terms():
    package = unchanged_stream_package()
    package["design_basis"]["components"] = ["A", "B", "C"]
    package["tolerances"] = {"composition_abs": 0.0}
    for stream in package["streams"]:
        stream["composition"] = {"A": 1.0, "B": 2**-53, "C": 2**-53}
    # Sequentially rounded addition would discard B and C and incorrectly pass.
    assert validate_process_package(package)["status"] == "FAIL"


def test_multi_stream_component_sum_retains_small_terms():
    package = unchanged_stream_package()
    package["tolerances"] = {"mass_relative": 0.0, "component_relative": 0.0}
    original = package["streams"][0]
    inlets = [
        {**original, "stream_id": f"IN-{index}", "total_mass_kg_h": mass, "enthalpy_kW": 0.0}
        for index, mass in enumerate([float(2**53), 1.0, 1.0])
    ]
    package["streams"] = [
        *inlets,
        {**package["streams"][1], "total_mass_kg_h": float(2**53 + 2), "enthalpy_kW": 0.0},
    ]
    package["equipment"][0]["inlet_stream_ids"] = [item["stream_id"] for item in inlets]
    result = validate_process_package(package)
    assert result["status"] == "PASS"
    assert result["metrics"]["max_component_balance_relative_error"] == 0.0
