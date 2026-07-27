from __future__ import annotations

import json
import tomllib
from pathlib import Path

import yaml

import tsao

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_VERSION = "0.1.0-alpha.10"
PEP440_VERSION = "0.1.0a10"
PYTHON_CLASSIFIERS = {
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
}


def test_alpha10_release_identity_is_consistent() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    identity = json.loads((ROOT / "reports/RELEASE_IDENTITY.json").read_text(encoding="utf-8"))
    complete = json.loads((ROOT / "reports/COMPLETE_DISTRIBUTION_REFERENCE.json").read_text(encoding="utf-8"))
    status = json.loads((ROOT / "reports/ALPHA10_SOURCE_CORE_STATUS.json").read_text(encoding="utf-8"))

    assert tsao.__version__ == PUBLIC_VERSION
    assert pyproject["project"]["version"] == PEP440_VERSION
    assert manifest["version"] == PUBLIC_VERSION
    assert citation["version"] == PUBLIC_VERSION
    assert str(citation["date-released"]) == "2026-07-27"
    assert identity["version"] == PUBLIC_VERSION
    assert identity["source_core"]["status"] == "reports/ALPHA10_SOURCE_CORE_STATUS.json"
    assert complete["version"] == PUBLIC_VERSION
    assert "alpha.10" in complete["reason"]
    assert status["version"] == PUBLIC_VERSION
    assert status["status"] == "QUALIFIED_ALPHA"


def test_project_metadata_and_requirements_are_in_lockstep() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = pyproject["project"]
    requirements = {
        line.strip()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    declared = set(project["dependencies"]) | set(project["optional-dependencies"]["dev"])
    assert requirements == declared
    assert PYTHON_CLASSIFIERS <= set(project["classifiers"])
    assert project["urls"]["Source"] == "https://github.com/SUNHAOJUN22/TSAO-PROCESSING-SKILL"
    assert project["urls"]["Issues"].endswith("/issues")


def test_performance_evidence_is_passing_and_result_stable() -> None:
    comparison = json.loads((ROOT / "reports/PERFORMANCE_COMPARISON_ALPHA10.json").read_text(encoding="utf-8"))
    assert comparison["pass"] is True
    assert comparison["optimized_version"] == PUBLIC_VERSION
    assert comparison["errors"] == []
    assert all(row["pass"] for row in comparison["comparisons"])
    assert all(row["result_digest_match"] for row in comparison["comparisons"])


def test_immutable_release_identities_are_packaged() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    verifier = (ROOT / "scripts/verify_wheel_contents.py").read_text(encoding="utf-8")
    required = (
        "reports/RELEASE_IDENTITY.json",
        "reports/ALPHA10_SOURCE_CORE_STATUS.json",
        "reports/COMPLETE_DISTRIBUTION_REFERENCE.json",
        "reports/SOURCE_CORE_MANIFEST.tsv",
        "reports/PERFORMANCE_BASELINE_ALPHA9.json",
        "reports/PERFORMANCE_OPTIMIZED_ALPHA10.json",
        "reports/PERFORMANCE_COMPARISON_ALPHA10.json",
    )
    for relative in required:
        assert f'"{relative}"' in pyproject
        assert f'/{relative}' in verifier


def test_current_alpha10_source_uses_staged_alpha11_qualification_pipeline() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    reports_index = (ROOT / "reports/README.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    matrix = (ROOT / "docs/CAPABILITY_MATRIX.md").read_text(encoding="utf-8")

    assert changelog.index("## 0.1.0-alpha.10") < changelog.index("## 0.1.0-alpha.9")
    assert "Current alpha.10 identities" in reports_index
    assert "ALPHA10_SOURCE_CORE_STATUS.json" in reports_index
    assert "name: TSAO alpha11 qualification" in workflow
    assert "[FINALIZE-ALPHA11]" in workflow
    assert "source-alpha.11.zip" in workflow
    assert "tsao-source-alpha11-" in workflow
    assert "benchmark_performance_v2.py" in workflow
    assert "compare_performance_v2.py" in workflow
    assert "generate_uiux_readme_assets.py" in workflow
    assert "status-alpha.10" in readme
    assert "status-alpha.10" in readme_zh
    assert "PERFORMANCE_RESULTS_START" in readme
    assert "PERFORMANCE_RESULTS_START" in readme_zh
    assert "0.1.0-alpha.10" in matrix
