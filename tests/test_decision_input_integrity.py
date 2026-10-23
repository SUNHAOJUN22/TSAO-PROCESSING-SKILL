"""Real input boundaries; all fixtures are synthetic software checks."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest

from skills.epdm.canonical_loader import CanonicalProjectLoadError, parse_project_json
from skills.epdm.state_generator import load_state_catalog
from skills.poe.package_audit import audit_process_package
from tsao.numeric_contract import finite
from tsao.project import audit_project, bootstrap_project
from tsao.science import balance_residual

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "poe_input_fixture", ROOT / "skills/poe/tests/test_poe_alpha6_package.py"
)
FIXTURE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FIXTURE)


@pytest.mark.parametrize("token", ["1e-999", "-1e-999", "1e999", "-1e999"])
def test_canonical_parser_rejects_unrepresentable_json_numbers(token: str) -> None:
    with pytest.raises(CanonicalProjectLoadError) as caught:
        parse_project_json('{"measurement":' + token + "}")
    assert caught.value.issue.phase == "json_parse"
    assert "finite" in caught.value.issue.message or "underflow" in caught.value.issue.message


@pytest.mark.parametrize("token", ["0e-999", "-0.0e-999", "5e-324", "-5e-324"])
def test_canonical_parser_keeps_true_zero_subnormals_and_integer_identity(token: str) -> None:
    value = parse_project_json('{"measurement":' + token + ',"count":9007199254740993}')
    assert value["measurement"] == float(token)
    assert math.copysign(1, value["measurement"]) == math.copysign(1, float(token))
    assert type(value["count"]) is int and value["count"] == 9007199254740993


@pytest.mark.parametrize("token", ["1e-999", "-1e-999"])
def test_canonical_cli_cannot_publish_an_erased_uncertainty(tmp_path: Path, token: str) -> None:
    source = ROOT / "skills/epdm/fixtures/v2_phase_a1_reference_project.json"
    text = source.read_text(encoding="utf-8")
    assert '"standard_uncertainty": 5.0' in text
    request = tmp_path / "project.json"
    request.write_text(
        text.replace('"standard_uncertainty": 5.0', '"standard_uncertainty": ' + token, 1),
        encoding="utf-8",
    )
    target = tmp_path / "published.json"
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "tsao.cli",
            "epdm",
            "canonicalize",
            "--file",
            str(request),
            "--out",
            str(target),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode != 0, process.stdout
    assert "underflow" in process.stderr
    assert not target.exists()


@pytest.mark.parametrize("record", ["manifest", "work-packages", "gate-events"])
@pytest.mark.parametrize("damage", ["duplicate", "underflow", "overflow"])
def test_project_audit_rejects_ambiguous_or_unrepresentable_records(
    tmp_path: Path, record: str, damage: str
) -> None:
    brief = tmp_path / "brief.yaml"
    brief.write_text("project_id: SYNTHETIC\ntitle: Generic process\n", encoding="utf-8")
    root = tmp_path / "project"
    bootstrap_project(brief, root)
    assert audit_project(root) == []
    if record == "manifest":
        path = root / "project_manifest.json"
        text = path.read_text(encoding="utf-8").rstrip()
        suffix = (
            ',"title":"overwritten"}'
            if damage == "duplicate"
            else ',"measurement":' + ("1e-999" if damage == "underflow" else "1e999") + "}"
        )
        text = text[:-1] + suffix
    elif record == "work-packages":
        path = root / "00_governance/work_packages.json"
        text = path.read_text(encoding="utf-8")
        replacement = (
            '"approval_status":"APPROVED","approval_status":"NOT_EVALUATED"'
            if damage == "duplicate"
            else '"approval_status":"NOT_EVALUATED","measurement":'
            + ("1e-999" if damage == "underflow" else "1e999")
        )
        text = text.replace('"approval_status": "NOT_EVALUATED"', replacement, 1)
    else:
        path = root / "00_governance/gate_events.jsonl"
        text = (
            '{"status":"FAIL","status":"PASS"}'
            if damage == "duplicate"
            else '{"measurement":' + ("1e-999" if damage == "underflow" else "1e999") + "}"
        )
    path.write_text(text + "\n", encoding="utf-8")
    issues = audit_project(root)
    assert issues
    assert any(term in " ".join(issues) for term in ("duplicate", "underflow", "finite"))


@pytest.mark.parametrize("damage", ["duplicate", "underflow", "negative-underflow", "overflow"])
def test_poe_file_audit_rejects_invalid_numbers_even_with_matching_integrity(
    tmp_path: Path, damage: str
) -> None:
    root = tmp_path / "package"
    FIXTURE.build_manifested_package(root)
    assert audit_process_package(root)["status"] == "PASS"
    path = root / "process_case.json"
    suffix = {
        "duplicate": ',"convergence":false,"convergence":true}',
        "underflow": ',"declared_loss_kg_h":1e-999}',
        "negative-underflow": ',"declared_loss_kg_h":-1e-999}',
        "overflow": ',"measurement":1e999}',
    }[damage]
    path.write_text(path.read_text(encoding="utf-8").rstrip()[:-1] + suffix, encoding="utf-8")
    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["structured_record_integrity"]["process_case"].update(
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    result = audit_process_package(root)
    assert result["status"] == "FAIL", result
    assert any(term in " ".join(result["errors"]) for term in ("duplicate", "underflow", "finite"))
    assert not any("mismatch" in error for error in result["errors"])
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize(
    "value",
    [
        "1e-999",
        "-1e-999",
        "١e-999",
        b"1e-999",
        bytearray(b"1e-999"),
        memoryview(b"1e-999"),
        Decimal("1e-999"),
        Fraction(1, 10**999),
    ],
)
def test_balance_input_coercion_never_erases_a_nonzero_quantity(value: object) -> None:
    with pytest.raises(ValueError, match="underflow"):
        balance_residual({}, {}, {"A": value})


@pytest.mark.parametrize("value", ["0e-999", "-0e-999", b"0e-999", Decimal(0), Fraction(0)])
def test_balance_keeps_previously_supported_zero_inputs(value: object) -> None:
    assert balance_residual({"A": value}, {}) == {"A": 0.0}


@pytest.mark.parametrize("token", ["1e-999999999999999999999999", "١e-999", "-١e-999"])
def test_strict_scalar_rejection_is_a_value_error_even_for_extreme_exponents(token: str) -> None:
    with pytest.raises(ValueError, match="underflow"):
        finite(token)


def test_caller_supplied_state_catalog_cannot_override_its_schema(tmp_path: Path) -> None:
    source = ROOT / "skills/epdm/data/state_variable_catalog_v2.json"
    text = source.read_text(encoding="utf-8")
    assert '"schema": "TSAO-EPDM-V2-STATE-CATALOG-1"' in text
    path = tmp_path / "catalog.json"
    path.write_text(
        text.replace(
            '"schema": "TSAO-EPDM-V2-STATE-CATALOG-1"',
            '"schema":"INVALID","schema":"TSAO-EPDM-V2-STATE-CATALOG-1"',
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate"):
        load_state_catalog(path)


@pytest.mark.parametrize(
    "suffix",
    [
        ',"measurement":1e-999}',
        ',"measurement":1e999}',
        ',"case_kind":"PROJECT_CASE","case_kind":"SYNTHETIC_REFERENCE_TEST"}',
    ],
)
def test_standalone_epdm_audit_uses_the_same_strict_file_contract(
    tmp_path: Path, suffix: str
) -> None:
    source = ROOT / "skills/epdm/fixtures/reference_cases.json"
    case = json.loads(source.read_text(encoding="utf-8"))["valid_case"]
    path = tmp_path / "case.json"
    path.write_text(json.dumps(case)[:-1] + suffix, encoding="utf-8")
    process = subprocess.run(
        [
            sys.executable,
            str(ROOT / "skills/epdm/scripts/audit_epdm.py"),
            "--file",
            str(path),
            "--case-only",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode == 2, process.stdout
    assert any(term in process.stderr for term in ("duplicate", "underflow", "finite"))
    assert "Traceback" not in process.stderr
