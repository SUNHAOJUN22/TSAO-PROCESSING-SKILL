from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tsao.distribution_policy import (
    DistributionBlockedError,
    assert_public_distribution_allowed,
    audit_public_distribution,
)

PUBLIC = {
    "confidentiality": "PUBLIC",
    "evidence_class": "SYNTHETIC_PUBLIC_FIXTURE",
    "license_scope": "PUBLIC_SYNTHETIC",
    "public_fixture_eligible": True,
}


def _registry(root: Path, record: dict[str, object]) -> None:
    data = root / "skills/poe/data"
    data.mkdir(parents=True)
    (data / "source_asset_registry.json").write_text(
        json.dumps(
            {"expected_asset_count": 1, "asset_files": ["source_asset_registry.part01.json"]}
        ),
        encoding="utf-8",
    )
    (data / "source_asset_registry.part01.json").write_text(
        json.dumps({"records": [record]}), encoding="utf-8"
    )


@pytest.mark.parametrize("field", ["confidentiality", "evidence_class", "license_scope"])
@pytest.mark.parametrize("value", ["UNKNOWN", "", "controlled_internal"])
def test_only_explicit_public_classification_can_be_exported(tmp_path, field, value):
    _registry(tmp_path, {**PUBLIC, field: value})
    audit = audit_public_distribution(tmp_path)
    assert audit.status == "BLOCKED_CONTROLLED_METADATA_CLASSIFICATION"
    assert audit.controlled_record_count == 1
    with pytest.raises(DistributionBlockedError):
        assert_public_distribution_allowed(tmp_path, artifact_kind="synthetic regression")


@pytest.mark.parametrize("value", [1, "true", None])
def test_public_eligibility_requires_the_exact_boolean(tmp_path, value):
    _registry(tmp_path, {**PUBLIC, "public_fixture_eligible": value})
    assert audit_public_distribution(tmp_path).controlled_record_count == 1


@pytest.mark.parametrize("public", [True, False])
def test_public_distribution_cli_obeys_same_allowlist(tmp_path, public):
    _registry(tmp_path, PUBLIC if public else {**PUBLIC, "license_scope": "UNREVIEWED"})
    result = subprocess.run(
        [sys.executable, "-m", "scripts.check_public_distribution", "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == (0 if public else 2)
    assert json.loads(result.stdout)["status"] == (
        "PASS" if public else "BLOCKED_CONTROLLED_METADATA_CLASSIFICATION"
    )
