"""Synthetic public-entry regressions; no fixture is engineering certification."""

import importlib.util
import json
from pathlib import Path

import pytest

from skills.poe.acceptance_status import derive_decision_tracks
from skills.poe.material_balance import evaluate_material_balance
from tsao.process_package import validate_process_package

ROOT = Path(__file__).resolve().parents[1]


def fixture_module(relative):
    spec = importlib.util.spec_from_file_location("fixture_" + Path(relative).stem, ROOT / relative)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


GENERIC = fixture_module("skills/process-general/tests/test_process_package_runtime.py")
BALANCE = fixture_module("skills/poe/tests/test_material_balance_v2.py")
DECISIONS = fixture_module("skills/poe/tests/test_acceptance_status_v2.py")


@pytest.mark.parametrize("area", ["package", "equipment", "controls", "hse", "acceptance"])
@pytest.mark.parametrize("status", ["FAIL", "HOLD", "CONDITIONAL", "NOT_EVALUATED"])
def test_nonpass_decisions_cannot_be_upgraded(area, status):
    package = GENERIC.valid_package()
    if area == "package":
        package["status"] = status
    elif area == "equipment":
        package["equipment"][0]["design_status"] = status
    elif area == "controls":
        package["controls"] = [
            {
                "loop_id": "L1",
                "status": status,
                "controlled_variable": "T",
                "manipulated_variable": "Q",
                "measurement_tag": "T1",
                "final_element_tag": "V1",
            }
        ]
    else:
        package[area][0]["status"] = status
    result = validate_process_package(package)
    assert result["status"] == ("FAIL" if status == "FAIL" else "HOLD")


def test_empty_process_never_qualifies_balances():
    package = GENERIC.valid_package()
    package.update(streams=[], equipment=[])
    assert validate_process_package(package)["status"] == "FAIL"
    package["profile"] = "METADATA_ONLY"
    result = validate_process_package(package)
    assert not result["pass"]
    assert result["balance_status"] == "NOT_EVALUATED"


@pytest.mark.parametrize("value", [10**400, 1.7e308, 5e-324])
def test_material_conversion_range_fails_closed(value):
    case = BALANCE.base_case()
    for stream in case["streams"]:
        stream["flow"].update(value=value, unit="t/s" if value > 1 else "kg/h")
    result = evaluate_material_balance(case)
    assert result["status"] == "FAIL"
    json.dumps(result, allow_nan=False)


def test_overflowing_generic_sum_never_passes():
    package = GENERIC.valid_package()
    for stream in package["streams"]:
        stream["total_mass_kg_h"] = 1.7e308
    extra_in = {**package["streams"][0], "stream_id": "S3"}
    extra_out = {**package["streams"][1], "stream_id": "S4"}
    package["streams"].extend([extra_in, extra_out])
    package["equipment"][0]["inlet_stream_ids"].append("S3")
    package["equipment"][0]["outlet_stream_ids"].append("S4")
    result = validate_process_package(package)
    assert result["status"] == "FAIL"
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize(
    "software",
    [
        {},
        {"errors": []},
        {"status": "FAIL", "errors": [], "holds": []},
        {"status": "PASS", "errors": [], "holds": [], "pass": "true"},
    ],
)
def test_missing_or_malformed_software_cannot_pass(software):
    requirements, acceptance, evidence, hse = DECISIONS.passing_records()
    result = derive_decision_tracks(
        software_result=software,
        requirement_trace=requirements,
        acceptance=acceptance,
        evidence_ledger=evidence,
        hse=hse,
    )
    assert result["software_integrity_status"] != "PASS"
    assert not result["pass"]


def test_sentinel_hash_is_not_artifact_verification():
    requirements, acceptance, evidence, hse = DECISIONS.passing_records()
    result = derive_decision_tracks(
        software_result={"status": "PASS", "errors": [], "holds": []},
        requirement_trace=requirements,
        acceptance=acceptance,
        evidence_ledger=evidence,
        hse=hse,
    )
    assert result["engineering_acceptance_status"] != "PASS"
    assert not result["pass"]


def bound_records(root):
    import hashlib

    requirements, acceptance, evidence, hse = DECISIONS.passing_records()
    for record in evidence["evidence"]:
        artifact = root / (record["evidence_id"] + ".txt")
        artifact.write_text(
            "synthetic test evidence for " + record["evidence_id"], encoding="utf-8"
        )
        record.update(
            artifact_path=artifact.name,
            artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
        )
    return requirements, acceptance, evidence, hse


@pytest.mark.parametrize(
    "damage", ["none", "tampered", "duplicate", "conflict", "malformed_ref", "symlink"]
)
def test_evidence_bytes_and_identity_are_verified(tmp_path, damage):
    requirements, acceptance, evidence, hse = bound_records(tmp_path)
    if damage == "tampered":
        (tmp_path / "E-1.txt").write_text("changed evidence", encoding="utf-8")
    if damage == "duplicate":
        evidence["evidence"].append(dict(evidence["evidence"][0]))
    if damage == "conflict":
        acceptance["status"] = "FAIL"
    if damage == "malformed_ref":
        requirements["requirements"][0]["evidence_ids"].append(7)
    if damage == "symlink":
        linked = tmp_path / "linked.txt"
        try:
            linked.symlink_to(tmp_path / "E-1.txt")
        except OSError:
            pytest.skip("host does not permit symlink creation")
        evidence["evidence"][0]["artifact_path"] = linked.name
    result = derive_decision_tracks(
        software_result={"status": "PASS", "errors": [], "holds": []},
        requirement_trace=requirements,
        acceptance=acceptance,
        evidence_ledger=evidence,
        hse=hse,
        artifact_root=tmp_path,
    )
    assert result["pass"] is (damage == "none")


def test_package_cli_refuses_failed_decision_and_duplicate_json(tmp_path):
    import subprocess
    import sys

    package = GENERIC.valid_package()
    package["equipment"][0]["design_status"] = "FAIL"
    target = tmp_path / "package.json"
    target.write_text(json.dumps(package), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "tsao.cli", "package", "audit", "--file", str(target)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert json.loads(result.stdout)["status"] == "FAIL"
    target.write_text('{"status":"FAIL","status":"PASS"}', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "tsao.cli", "package", "audit", "--file", str(target)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "duplicate JSON key" in result.stderr


@pytest.mark.parametrize("damaged", ["absolute_tolerance", "relative_tolerance"])
def test_nonfinite_or_underflowing_tolerances_cannot_close_balance(damaged):
    case = BALANCE.base_case()
    if damaged == "absolute_tolerance":
        case["balance"][damaged].update(value=1e308, unit="t/s")
    else:
        case["balance"][damaged] = 5e-324
    assert evaluate_material_balance(case)["status"] == "FAIL"


def test_large_sum_cancellation_preserves_small_residual():
    from tsao.numeric_contract import finite_sum

    assert finite_sum([1e308, 1e308, 1.0, -1e308, -1e308]) == 1.0
    assert finite_sum([1e308, 1e308, 5e-324, -1e308, -1e308]) == 5e-324
    with pytest.raises(ValueError, match="finite"):
        finite_sum([1e308, 1e308])


@pytest.mark.parametrize("token", ["1e-999", "-1e-999", "1e999"])
def test_json_numeric_range_checked_before_float_rounding(token):
    from tsao.json_contract import loads_strict

    with pytest.raises(ValueError):
        loads_strict('{"value":' + token + '}')
    assert loads_strict('{"value":0e-999}') == {"value": 0.0}


def test_cli_rejects_json_underflow_before_package_audit(tmp_path, capsys):
    from tsao.cli import main

    file = tmp_path / "input.json"
    file.write_text('{"tolerance":1e-999}', encoding="utf-8")
    assert main(["package", "audit", "--file", str(file)]) != 0
    assert "underflow" in capsys.readouterr().err
