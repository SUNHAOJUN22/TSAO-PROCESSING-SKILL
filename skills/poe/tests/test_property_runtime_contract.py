from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from skills.poe.core import audit_process_package, qualify_property_method, validate_process_case
from skills.poe.tests.test_poe_alpha6_p0 import qualified_property, valid_case
from skills.poe.tests.test_poe_alpha6_package import build_manifested_package

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas/property_method.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("field", SCHEMA["required"])
def test_required_property_fields_cannot_be_omitted_at_runtime(field):
    case = valid_case()
    del case["property_method"][field]
    assert not Draft202012Validator(SCHEMA).is_valid(case["property_method"])
    result = qualify_property_method(case["property_method"], case["property_query"])
    # Missing components also makes the declared composition domain unresolved.
    assert result["status"] == ("FAIL" if field in {"method", "components"} else "HOLD")
    assert not result["pass"]
    assert not validate_process_case(case)["pass"]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("temperature_K", None),
        ("pressure_Pa", None),
        ("polymer_mass_fraction", None),
        ("composition_domain", None),
        ("selection_basis", None),
        ("selection_basis", ""),
        ("unit_system", None),
        ("extrapolation_status", None),
        ("benchmarks", [{"property": "density", "source": {"unverified": "source"}, "points": 3}]),
        ("custom_equations", None),
        ("unrecognized_qualification_override", "PASS"),
    ],
)
def test_invalid_property_contracts_fail_before_process_qualification(field, invalid):
    case = valid_case()
    case["property_method"][field] = invalid
    assert not Draft202012Validator(SCHEMA).is_valid(case["property_method"])
    result = qualify_property_method(case["property_method"], case["property_query"])
    assert result["status"] == "FAIL"
    assert not result["pass"]
    assert result["scientific_approval"] == "NOT_EVALUATED"
    downstream = validate_process_case(case)
    assert downstream["status"] == "FAIL"
    assert any("property method:" in error for error in downstream["errors"])
    assert downstream["engineering_approval"] == "NOT_EVALUATED"


@pytest.mark.parametrize(
    ("field", "value"),
    [("temperature_K", 500.0), ("pressure_Pa", 30000000.0), ("polymer_mass_fraction", 0.5)],
)
def test_outside_qualified_domain_holds_and_null_cannot_erase_the_domain(field, value):
    case = valid_case()
    case["property_query"][field] = value
    # The explicit declared endpoints, rather than the implementation's range
    # helper, establish that the process query is outside this fixture's domain.
    assert value > case["property_method"][field][1]
    assert (
        qualify_property_method(case["property_method"], case["property_query"])["status"] == "HOLD"
    )
    assert validate_process_case(case)["status"] == "HOLD"
    case["property_method"][field] = None
    assert (
        qualify_property_method(case["property_method"], case["property_query"])["status"] == "FAIL"
    )
    assert validate_process_case(case)["status"] == "FAIL"


def test_optional_custom_equations_and_declared_holds_keep_their_meaning():
    record = qualified_property()
    assert "custom_equations" not in record
    assert qualify_property_method(record)["status"] == "PASS"
    record["custom_equations"] = []
    assert Draft202012Validator(SCHEMA).is_valid(record)
    assert qualify_property_method(record)["status"] == "PASS"
    record["method"] = "CUSTOM"
    assert qualify_property_method(record)["status"] == "HOLD"
    record["custom_equations"] = ["synthetic reference equation with coefficient provenance"]
    assert qualify_property_method(record)["status"] == "PASS"
    case = valid_case()
    case["property_method"] = dict(record, extrapolation_status="DECLARED_HOLD")
    assert Draft202012Validator(SCHEMA).is_valid(case["property_method"])
    assert validate_process_case(case)["status"] == "HOLD"


def _write_record_with_current_integrity(root: Path, name: str, record: dict) -> None:
    path = root / f"{name}.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["structured_record_integrity"][name] = {
        "path": path.name,
        "bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


def test_manifested_process_package_cannot_qualify_an_unknown_property_domain(tmp_path):
    root = tmp_path / "synthetic-package"
    build_manifested_package(root)
    case_path = root / "process_case.json"
    case = json.loads(case_path.read_text(encoding="utf-8"))
    case["property_query"] = {"temperature_K": 370.0}
    _write_record_with_current_integrity(root, "process_case", case)
    assert audit_process_package(root)["status"] == "PASS"

    case["property_query"]["temperature_K"] = 500.0
    _write_record_with_current_integrity(root, "process_case", case)
    assert audit_process_package(root)["status"] == "HOLD"

    case["property_method"]["temperature_K"] = None
    _write_record_with_current_integrity(root, "property_method", case["property_method"])
    _write_record_with_current_integrity(root, "process_case", case)
    result = audit_process_package(root)
    assert result["status"] == "FAIL"
    assert any("temperature_K" in error for error in result["errors"])
    assert not any("mismatch" in error for error in result["errors"])

    del case["property_method"]["temperature_K"]
    _write_record_with_current_integrity(root, "property_method", case["property_method"])
    _write_record_with_current_integrity(root, "process_case", case)
    result = audit_process_package(root)
    assert result["status"] == "HOLD"
    assert not result["errors"]
