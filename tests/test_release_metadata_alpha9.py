from __future__ import annotations

import json
import tomllib
from pathlib import Path

import yaml

import tsao

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_VERSION = "0.1.0-alpha.9"
PEP440_VERSION = "0.1.0a9"
PYTHON_CLASSIFIERS = {
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
}


def test_alpha9_release_identity_is_consistent() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    citation = yaml.safe_load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    identity = json.loads((ROOT / "reports/RELEASE_IDENTITY.json").read_text(encoding="utf-8"))
    complete = json.loads(
        (ROOT / "reports/COMPLETE_DISTRIBUTION_REFERENCE.json").read_text(encoding="utf-8")
    )
    status = json.loads(
        (ROOT / "reports/ALPHA9_SOURCE_CORE_STATUS.json").read_text(encoding="utf-8")
    )

    assert tsao.__version__ == PUBLIC_VERSION
    assert pyproject["project"]["version"] == PEP440_VERSION
    assert manifest["version"] == PUBLIC_VERSION
    assert citation["version"] == PUBLIC_VERSION
    assert citation["date-released"] == "2026-07-26"
    assert identity["version"] == PUBLIC_VERSION
    assert identity["source_core"]["status"] == "reports/ALPHA9_SOURCE_CORE_STATUS.json"
    assert complete["version"] == PUBLIC_VERSION
    assert "alpha.9" in complete["reason"]
    assert "alpha.7" not in complete["reason"]
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


def test_current_release_docs_and_ci_are_alpha9() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    reports_index = (ROOT / "reports/README.md").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_zh = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
    matrix = (ROOT / "docs/CAPABILITY_MATRIX.md").read_text(encoding="utf-8")

    assert changelog.index("## 0.1.0-alpha.9") < changelog.index("## 0.1.0-alpha.8")
    assert "Unreleased hardening" not in changelog
    assert "Current alpha.9 identities" in reports_index
    assert "ALPHA9_SOURCE_CORE_STATUS.json" in reports_index
    assert "Current alpha.7 identities" not in reports_index
    assert "name: TSAO alpha9 qualification" in workflow
    assert "[FINALIZE-ALPHA9]" in workflow
    assert "source-alpha.9.zip" in workflow
    assert "tsao-source-alpha9-" in workflow
    assert "alpha8" not in workflow.casefold()
    assert "status-alpha.9" in readme
    assert "status-alpha.9" in readme_zh
    assert "0.1.0-alpha.9" in matrix
